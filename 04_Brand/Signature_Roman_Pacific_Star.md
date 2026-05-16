---
aliases:
  - Подпись Роман PS
  - Email signature Roman
tags:
  - зона/бренд
  - бренд/pacific-star
  - тип/шаблон
---

# Email-подпись — Хмелев Роман Александрович (Pacific Star)

> Персонализированная подпись Романа на направлении D «Печать Меридиана». Шаблон для подстановки данных других сотрудников — `Pacific_Star_Email_Signature.md`. Готовый файл для копирования в Apple Mail — `Signature_Roman_Pacific_Star.html`.
>
> Версия 2.0 (12 мая 2026) · решение `30_Decisions/2026-05-12-PS_brand_direction.md`.

## Данные подстановки

| Поле | Значение |
|---|---|
| ФИО | Хмелев Роман Александрович |
| Должность | Коммерческий директор |
| Прямой телефон | +7 (914) 728-58-80 |
| Email | office@pacificstar.ru |
| Логотип | `Logo_Pacific_Star_Mark.svg` → конвертирован в `Logo_Pacific_Star_Mark.png` (256×256) → встроен как base64 в HTML, 64×64 px в подписи |
| ИНН ООО | 2508025295 |
| КПП | 250801001 |
| ОГРН | 1022500704863 |
| Юр. адрес | 692953, Приморский край, г. Находка, ул. Луговая, д. 14 |
| ГосЛог | заявление подано 09.03.2026 |

## Дизайн (направление D «Печать Меридиана»)

Подпись построена по схеме «лицо + знак»:

- **Левая колонка** — имя/должность/контакты Романа.
  - Имя — Inter Display Bold 15 px, Stamp Ink `#1F2A35`.
  - Должность — Golos Text Regular 12 px, Steel `#5C6470`.
  - Контакты — Golos Text Regular 13 px, с буквенными префиксами Т / E / W в Steel.
  - Тонкая вертикаль Steel разделяет колонки.
- **Правая колонка** — фирменный знак.
  - Сверху — упрощённая метка `Logo_Pacific_Star_Mark.svg` v2 (облегчённый крест, stroke 8/5), отображается 64×64 px. Встроена в HTML как `<img src="data:image/png;base64,…">` из `Logo_Pacific_Star_Mark.png` 256×256, потому что Apple Mail при копировании из Safari вычищает inline SVG, а PNG-base64 переживает copy-paste и работает во всех клиентах включая старый Outlook.
  - Под меткой — wordmark «Тихоокеанская Звезда» (Inter Display Bold 14 px, Stamp Ink).
  - Под wordmark — слоган «Логистика на Дальнем Востоке» (Golos Text Italic 11 px, Steel).
- **Нижняя плашка** — горизонталь Steel `#5C6470` 1 px + блок реквизитов Golos Text 11 px Steel. Три строки: юр. название + ИНН/КПП/ОГРН, юр. адрес, статус ГосЛог.

Палитра везде: только Stamp Ink + Steel + Document (фон). Без Customs Orange — акцент в подписи делает контраст между знаком и текстом, дополнительный цвет лишний.

## HTML-подпись (копировать целиком)

```html
<table cellpadding="0" cellspacing="0" border="0" style="font-family: 'Inter Display', 'Inter', Arial, sans-serif; color: #1F2A35; line-height: 1.5;">
  <tr>
    <td style="padding: 0 22px 0 0; vertical-align: top; border-right: 1px solid #5C6470;">
      <div style="font-size: 15px; font-weight: 700; color: #1F2A35; margin-bottom: 2px;">Хмелев Роман Александрович</div>
      <div style="font-family: 'Golos Text', Arial, sans-serif; font-size: 12px; color: #5C6470; margin-bottom: 14px;">Коммерческий директор</div>
      <div style="font-family: 'Golos Text', Arial, sans-serif; font-size: 13px; color: #1F2A35; line-height: 1.75;">
        <span style="display: inline-block; width: 22px; color: #5C6470; font-weight: 500;">Т</span> <a href="tel:+79147285880" style="color: #1F2A35; text-decoration: none;">+7 (914) 728-58-80</a><br>
        <span style="display: inline-block; width: 22px; color: #5C6470; font-weight: 500;">E</span> <a href="mailto:office@pacificstar.ru" style="color: #1F2A35; text-decoration: none;">office@pacificstar.ru</a><br>
        <span style="display: inline-block; width: 22px; color: #5C6470; font-weight: 500;">W</span> <a href="https://pacificstar.ru" style="color: #1F2A35; text-decoration: none;">pacificstar.ru</a>
      </div>
    </td>
    <td style="padding: 0 0 0 22px; vertical-align: top;">
      <img src="data:image/png;base64,[BASE64_PNG_256x256]" width="64" height="64" alt="Pacific Star" style="display: block; margin-bottom: 10px;">
      <div style="font-size: 14px; font-weight: 700; color: #1F2A35; line-height: 1.2;">Тихоокеанская Звезда</div>
      <div style="font-family: 'Golos Text', Arial, sans-serif; font-size: 11px; font-style: italic; color: #5C6470; margin-top: 2px;">Логистика на Дальнем Востоке</div>
    </td>
  </tr>
  <tr>
    <td colspan="2" style="padding-top: 16px;">
      <div style="border-top: 1px solid #5C6470; padding-top: 10px; font-family: 'Golos Text', Arial, sans-serif; font-size: 11px; color: #5C6470; line-height: 1.6;">
        ООО Компания «Тихоокеанская Звезда» · ИНН 2508025295 · КПП 250801001 · ОГРН 1022500704863<br>
        Юр. адрес: 692953, Приморский край, г. Находка, ул. Луговая, д. 14<br>
        Реестр экспедиторов ГосЛог: заявление подано 09.03.2026
      </div>
    </td>
  </tr>
</table>
```

## Plain-text подпись (fallback для мобильных и старых клиентов)

```
—
Хмелев Роман Александрович
Коммерческий директор

Тихоокеанская Звезда
Логистика на Дальнем Востоке

Т: +7 (914) 728-58-80
E: office@pacificstar.ru
W: pacificstar.ru

ООО Компания «Тихоокеанская Звезда»
ИНН 2508025295 · КПП 250801001 · ОГРН 1022500704863
Юр. адрес: 692953, Приморский край, г. Находка, ул. Луговая, д. 14
Реестр экспедиторов ГосЛог: заявление подано 09.03.2026
```

## Установка в Apple Mail

1. Открой `Signature_Roman_Pacific_Star.html` в Safari (двойной клик в Finder).
2. Выдели подпись с курсором — от имени до строки про ГосЛог.
3. Cmd+C.
4. Mail → Настройки → Подписи → плюс на ящике office@pacificstar.ru → имя подписи «Pacific Star v2».
5. Вставь в поле подписи (если режим текстовый — переключи на Rich Text через правый клик).
6. Сними галочку «Использовать всегда тот же шрифт».
7. Под почтовым ящиком в выпадающем списке — «Выбрать подпись Pacific Star v2» по умолчанию.

В Outlook/Gmail HTML вставляется через настройки подписи в веб-интерфейсе. Знак встроен как PNG-base64 (не SVG) — это переживает copy-paste из Safari в Apple Mail и отображается во всех клиентах, включая старый Outlook. Размер base64-блока в HTML — около 10 КБ, ниже типового лимита подписи у всех почтовых сервисов.

## Что остаётся открыто

- ⚠️ Когда команда подключится к @pacificstar.ru (Татьяна, Ирина, РОП, log1/log2) — продублировать файл под каждого: меняются только 4 поля сверху (ФИО, должность, прямой телефон, email), реквизиты компании и блок справа те же.
- ⚠️ Тест-рендер в Gmail / Yandex.Mail / Outlook web — Роман делает после первой реальной отправки.
- ✅ PNG-версия логотипа собрана: `Logo_Pacific_Star_Mark.png` 256×256, встроена в HTML-подпись как base64. Не требует внешнего хостинга, не ломается при пересылке писем.

---

<!-- AUTO-LINK -->
**См. также:** [[Pacific_Star]] | [[Pacific_Star_Brand_System]] | [[Pacific_Star_Requisites]] | [[Logo_Pacific_Star_Mark]] | [[CLAUDE]]
