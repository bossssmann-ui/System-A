// ============================================================
// Cowork Voice Bot — Telegram → Whisper → GitHub Obsidian Vault
// Deploy to Cloudflare Workers (free tier)
//
// Behaviour:
//   • Accepts messages from one whitelisted Telegram user_id.
//   • Voice   → Whisper transcription → appended to 90_Inbox/YYYY-MM-DD.md
//   • Text    → appended to 90_Inbox/YYYY-MM-DD.md
//   • Photo   → caption stored, file_id noted, reference appended
//   • Reacts with ✅ on success, ⚠️ on error, ⛔ on wrong user.
//
// Environment variables (Worker → Settings → Variables):
//   TELEGRAM_BOT_TOKEN      — secret
//   OPENAI_API_KEY          — secret
//   GITHUB_TOKEN            — secret (fine-grained PAT, repo Contents R/W)
//   WEBHOOK_SECRET          — secret (pick any random string yourself)
//   GITHUB_REPO             — plain   "bossssmann-ui/System-A"
//   GITHUB_BRANCH           — plain   "main"
//   ALLOWED_TG_USER_ID      — plain   "123456789"
// ============================================================

export default {
  async fetch(request, env, ctx) {
    // Webhook security: Telegram forwards our secret back in this header.
    const secret = request.headers.get('x-telegram-bot-api-secret-token');
    if (secret !== env.WEBHOOK_SECRET) {
      return new Response('forbidden', { status: 403 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response('bad request', { status: 400 });
    }

    const message = update.message || update.edited_message;
    if (!message) return new Response('ok');

    // Whitelist check — only the owner can use this bot.
    const userId = String(message.from?.id ?? '');
    if (userId !== String(env.ALLOWED_TG_USER_ID)) {
      ctx.waitUntil(sendMessage(env, message.chat.id, '⛔ not authorized'));
      return new Response('ok');
    }

    // Respond 200 immediately; do heavy work after response.
    ctx.waitUntil(handleMessage(env, message));
    return new Response('ok');
  },
};

// ------------------------------------------------------------
// Main router
// ------------------------------------------------------------
async function handleMessage(env, message) {
  try {
    let entry;
    if (message.voice) {
      entry = await handleVoice(env, message);
    } else if (message.audio) {
      entry = await handleVoice(env, message, message.audio);
    } else if (message.text) {
      entry = handleText(message);
    } else if (message.photo) {
      entry = handlePhoto(message);
    } else {
      await reactTo(env, message, '❓');
      return;
    }

    await appendToInbox(env, entry);
    await reactTo(env, message, '✅');
  } catch (err) {
    console.error('handleMessage error:', err);
    await reactTo(env, message, '⚠️');
    await sendMessage(env, message.chat.id, `⚠️ ${err.message}`);
  }
}

// ------------------------------------------------------------
// Handlers per message type
// ------------------------------------------------------------
async function handleVoice(env, message, audioOverride) {
  const audio = audioOverride || message.voice;
  const fileId = audio.file_id;

  // 1. Resolve Telegram file URL
  const fileInfo = await tgApi(env, 'getFile', { file_id: fileId });
  const fileUrl = `https://api.telegram.org/file/bot${env.TELEGRAM_BOT_TOKEN}/${fileInfo.file_path}`;

  // 2. Download audio
  const audioResp = await fetch(fileUrl);
  if (!audioResp.ok) throw new Error(`telegram file fetch failed: ${audioResp.status}`);
  const audioBlob = await audioResp.blob();

  // 3. Send to OpenAI Whisper
  const form = new FormData();
  form.append('file', audioBlob, 'voice.oga');
  form.append('model', 'whisper-1');
  // Oставлю язык auto — Whisper сам определит. Если надо: form.append('language', 'ru');

  const whisperResp = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.OPENAI_API_KEY}` },
    body: form,
  });
  if (!whisperResp.ok) {
    const errText = await whisperResp.text();
    throw new Error(`whisper failed: ${whisperResp.status} ${errText.slice(0, 200)}`);
  }
  const { text } = await whisperResp.json();

  return formatEntry('voice', text, { duration: audio.duration });
}

function handleText(message) {
  return formatEntry('text', message.text);
}

function handlePhoto(message) {
  const caption = message.caption || '(no caption)';
  const largest = message.photo[message.photo.length - 1];
  return formatEntry('photo', caption, { file_id: largest.file_id });
}

function formatEntry(kind, body, meta = {}) {
  const hhmm = new Date().toISOString().slice(11, 16);
  const metaStr = Object.keys(meta).length
    ? '  \n_' + Object.entries(meta).map(([k, v]) => `${k}: ${v}`).join(' · ') + '_'
    : '';
  return `### ${hhmm} — ${kind}\n\n${body.trim()}${metaStr}\n`;
}

// ------------------------------------------------------------
// GitHub writer
// ------------------------------------------------------------
async function appendToInbox(env, entry) {
  const today = new Date().toISOString().slice(0, 10);
  const path = `90_Inbox/${today}.md`;
  const branch = env.GITHUB_BRANCH || 'main';
  const url = `https://api.github.com/repos/${env.GITHUB_REPO}/contents/${path}`;
  const headers = {
    Authorization: `Bearer ${env.GITHUB_TOKEN}`,
    'User-Agent': 'cowork-voice-bot',
    Accept: 'application/vnd.github+json',
  };

  // Try to fetch existing file (to get sha for update)
  let existing = `# ${today}\n\n> Inbox дня. Наполняется ботом, разбирается в еженедельном обзоре.\n\n`;
  let sha;
  const getResp = await fetch(`${url}?ref=${branch}`, { headers });
  if (getResp.ok) {
    const data = await getResp.json();
    sha = data.sha;
    existing = b64decodeUtf8(data.content);
  } else if (getResp.status !== 404) {
    throw new Error(`github get failed: ${getResp.status}`);
  }

  const newContent = existing.endsWith('\n') ? existing + '\n' + entry : existing + '\n\n' + entry;

  const body = {
    message: `inbox: ${today}`,
    content: b64encodeUtf8(newContent),
    branch,
  };
  if (sha) body.sha = sha;

  const putResp = await fetch(url, {
    method: 'PUT',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!putResp.ok) {
    const errText = await putResp.text();
    throw new Error(`github put failed: ${putResp.status} ${errText.slice(0, 200)}`);
  }
}

// ------------------------------------------------------------
// Telegram helpers
// ------------------------------------------------------------
async function tgApi(env, method, payload) {
  const resp = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const json = await resp.json();
  if (!json.ok) throw new Error(`tg ${method} failed: ${json.description}`);
  return json.result;
}

async function sendMessage(env, chatId, text) {
  try {
    await tgApi(env, 'sendMessage', { chat_id: chatId, text });
  } catch (e) {
    console.error('sendMessage failed', e);
  }
}

async function reactTo(env, message, emoji) {
  try {
    await tgApi(env, 'setMessageReaction', {
      chat_id: message.chat.id,
      message_id: message.message_id,
      reaction: [{ type: 'emoji', emoji }],
    });
  } catch (e) {
    // setMessageReaction may fail on older Telegram versions; fall back silently.
    console.warn('reaction failed', e.message);
  }
}

// ------------------------------------------------------------
// UTF-8 safe base64 (GitHub expects base64 with UTF-8)
// ------------------------------------------------------------
function b64encodeUtf8(str) {
  const bytes = new TextEncoder().encode(str);
  let binary = '';
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary);
}

function b64decodeUtf8(b64) {
  const binary = atob(b64.replace(/\n/g, ''));
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return new TextDecoder().decode(bytes);
}
