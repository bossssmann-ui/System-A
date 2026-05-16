---
aliases:
  - Email-подпись Pacific Star
  - Подпись писем Тихоокеанская Звезда
tags:
  - зона/бренд
  - бренд/pacific-star
  - тип/шаблон
---

# Email-подпись Тихоокеанская Звезда

> Готовые HTML и plain-text подписи для всех сотрудников Pacific Star. Копируем в Apple Mail / Outlook / Gmail и используем по умолчанию во всех исходящих письмах.
>
> Цвета и шрифты — из [[Pacific_Star_Brand_System]].

---

## Заполни перед использованием

Каждый сотрудник заменяет в шаблоне свои данные:

| Поле | Пример |
|---|---|
| Имя сотрудника | Хмелев Роман [Отчество] |
| Должность | Директор |
| Прямой телефон | +7 (XXX) XXX-XX-XX |
| Email | name@pacificstar.ru |

Реквизиты компании одинаковые у всех — менять не нужно.

---

## HTML-подпись (копировать целиком)

Используется в большинстве современных почтовых клиентов. Скопировать ниже HTML-блок и вставить в "Подпись" (HTML-режим).

```html
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; line-height: 1.5; color: #1A1A1A;">
  <tr>
    <td style="padding-right: 16px; vertical-align: top; border-right: 3px solid #002B5C;">
      <span style="font-family: 'Manrope', Arial, sans-serif; font-size: 16px; font-weight: 700; color: #002B5C;">Хмелев Роман [Отчество]</span><br>
      <span style="font-size: 13px; color: #5A6A7A;">Директор</span>
    </td>
    <td style="padding-left: 16px; vertical-align: top;">
      <span style="font-size: 14px; font-weight: 600; color: #002B5C;">ООО Компания «Тихоокеанская Звезда»</span><br>
      <span style="font-size: 13px; color: #5A6A7A;">Логистика на Дальнем Востоке</span><br>
      <br>
      <span style="font-size: 13px; color: #1A1A1A;">📞 <a href="tel:+7XXXXXXXXXX" style="color: #1A1A1A; text-decoration: none;">+7 (XXX) XXX-XX-XX</a></span><br>
      <span style="font-size: 13px; color: #1A1A1A;">✉ <a href="mailto:name@pacificstar.ru" style="color: #1A1A1A; text-decoration: none;">name@pacificstar.ru</a></span><br>
      <span style="font-size: 13px; color: #1A1A1A;">🌐 <a href="https://pacificstar.ru" style="color: #002B5C; text-decoration: none; font-weight: 600;">pacificstar.ru</a></span>
    </td>
  </tr>
  <tr>
    <td colspan="2" style="padding-top: 12px; border-top: 1px solid #E8EEF2; margin-top: 12px;">
      <span style="font-size: 11px; color: #5A6A7A;">
        ООО Компания «Тихоокеанская Звезда» · ИНН: TBD · ОГРН: TBD<br>
        Юридический адрес: TBD<br>
        Реестр экспедиторов ГосЛог: № TBD (заявление подано 09.03.2026)
      </span>
    </td>
  </tr>
</table>
```

> **Примечание:** в подписи стоят эмоджи 📞 ✉ 🌐 для контактов — это норма в email-подписях, не нарушает принцип "без эмоджи в деловой переписке". Эмоджи здесь — навигация, а не настроение. Альтернатива — заменить на текст "Тел.:", "Email:", "Сайт:".

---

## Plain-text подпись (для тех, кто не любит HTML)

Используется как fallback или в простых письмах. Также пригодится при отправке писем-боев / рассылок:

```
—
Хмелев Роман [Отчество]
Директор
ООО Компания «Тихоокеанская Звезда»
Логистика на Дальнем Востоке

Тел.:  +7 (XXX) XXX-XX-XX
Email: name@pacificstar.ru
Сайт:  pacificstar.ru

ИНН: TBD · ОГРН: TBD
Юр. адрес: TBD
```

---

## Как поставить подпись по умолчанию

### Apple Mail (macOS)

1. Mail → Настройки (Cmd + ,) → Подписи.
2. Выбери почтовый ящик слева, нажми + добавить.
3. Назови подпись "Pacific Star".
4. **HTML-вариант:** правым кликом по полю подписи → "Параграф" → "HTML"; вставь HTML-блок.
   Если HTML-режим недоступен в твоей версии Mail — используй plain-text вариант.
5. Снизу — "Выбрать подпись по умолчанию" → Pacific Star.
6. Закрой настройки. Создай новое письмо — должна стоять подпись.

### Outlook (Windows / Mac)

1. Файл → Параметры → Почта → Подписи.
2. Создать новую: "Pacific Star".
3. В редакторе подписей вставить HTML-блок (Outlook понимает HTML).
4. В правом верхнем углу — "Выбрать подпись по умолчанию для новых сообщений" и "ответов".
5. Сохранить.

### Gmail (веб)

1. Gmail → ⚙ Настройки → Все настройки → Подпись.
2. Создать новую "Pacific Star".
3. Скопировать HTML-блок и вставить в редактор (Gmail вставит его как форматированный текст).
4. Внизу страницы — "Подпись по умолчанию": для новых писем + для ответов.
5. Сохранить.

### iPhone (Apple Mail)

1. Настройки → Почта → Подпись.
2. Выбрать почтовый ящик "Тихоокеанская Звезда" (если у тебя несколько ящиков).
3. Вставить **plain-text вариант** — на iPhone HTML-подписи поддерживаются плохо.
4. Сохранить.

---

## Подпись для Татьяны и Ирины (когда подключим к почте Pacific Star)

Заменить в шаблоне:

**Татьяна:**
- Имя: TBD — спросить у неё ФИО.
- Должность: Диспетчер.
- Email: tatyana@pacificstar.ru (создать ящик).

**Ирина:**
- Имя: Ирина [Отчество].
- Должность: Руководитель отдела логистики.
- Email: irina@pacificstar.ru (создать ящик).

---

## Что нужно проверить перед массовым внедрением

- [x] ИНН ООО Компания «Тихоокеанская Звезда» — **2508025295** (получено от Романа 12.05.26).
- [x] ОГРН — **1022500704863** (получено от Романа 12.05.26).
- [x] КПП — **250801001** (получено от Романа 12.05.26).
- [x] Юридический адрес — **692953, Приморский край, г. Находка, ул. Луговая, д. 14** (получено от Романа 12.05.26).
- [x] Реестровый номер ГосЛог — пока используем заглушку "заявление подано 09.03.2026" (по решению Романа от 12.05.26).
- [ ] Реальные email-адреса для каждого сотрудника (создать @pacificstar.ru если нет).
- [ ] Тестовая отправка на свой почтовый ящик и в Gmail, Yandex.Mail, Outlook — проверить что HTML рендерится корректно.

> Персональный готовый файл подписи Романа: [[Signature_Roman_Pacific_Star]].

---

## Что добавить в подпись после регистрации ТЗ

Когда логотип финализирован и зарегистрирован в Роспатенте (задача #23) — добавляем в HTML-подпись лого 32 px по высоте слева:

```html
<td style="padding-right: 16px; vertical-align: top;">
  <img src="https://pacificstar.ru/static/logo_email.png" alt="Pacific Star" width="120" style="display: block;">
</td>
```

(положить файл `logo_email.png` 240×80 px на сайт после доработки логотипа).

---

<!-- AUTO-LINK -->
**См. также:** [[Карта системы]] | [[Pinned Facts|Зафиксированные факты]] | [[Multi_Agent_Architecture|Архитектура]]

<!-- AUTO-ZONE-START -->
**Соседи по зоне:** [[Pacific_Star]] | [[Pacific_Star_Brand_System]] | [[Brand_Project]]
<!-- AUTO-ZONE-END -->
