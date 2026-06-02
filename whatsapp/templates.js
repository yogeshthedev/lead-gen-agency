/**
 * templates.js
 * WhatsApp message templates per business category.
 * Personalised with business name, city, your name.
 * Keep messages SHORT — WhatsApp is conversational, not email.
 */

const templates = {

  "chartered accountants": [
    // Day 1
    (name, city, yourName) =>
`Hi,

I came across *${name}* while searching for CA firms in ${city}.

I help CA firms get a professional website that brings in new clients from Google. Before I share more info, are you interested in upgrading your online presence?

Just reply with a quick 'Yes' or 'No'.

— ${yourName}`,

    // Day 4 follow-up
    (name, city, yourName) =>
`Hi again,

Just following up on my last message.

I can help *${name}* attract more clients online with a new website. Are you interested in discussing this?

A simple 'Yes' or 'No' is perfectly fine!

— ${yourName}`,

    // Day 8 final
    (name, city, yourName) =>
`Hi,

Last message from my side — I don't want to bother you!

If *${name}* ever wants to improve their online presence, I'm here. Otherwise, I won't reach out again.

— ${yourName}`,
  ],

  "restaurants": [
    (name, city, yourName) =>
`Hi,

I noticed *${name}* doesn't have a modern website yet.

I build websites for restaurants in ${city} to help get more bookings. Are you currently interested in upgrading your online presence?

Just reply with a quick 'Yes' or 'No'.

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up on my last message.

I can help *${name}* get more customers from Google with a new website. Are you interested in this?

A simple 'Yes' or 'No' works for me!

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last message from my side.

If *${name}* ever wants a website to drive more bookings, do reach out. Otherwise, I'll stop messaging here. 🙏

— ${yourName}`,
  ],

  "clinics": [
    (name, city, yourName) =>
`Hi,

I came across *${name}* while looking for clinics in ${city} and noticed your website could use an upgrade.

I help clinics get more patient bookings online. Are you interested in upgrading your online presence right now?

Just reply with a quick 'Yes' or 'No'.

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up on my last message.

I can help *${name}* attract more patients from Google with a professional website. Are you open to discussing this?

A simple 'Yes' or 'No' is perfectly fine!

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last message from me about *${name}*.

Whenever you're ready to grow your online presence, I'm here. Otherwise, I won't bother you again. 🙏

— ${yourName}`,
  ],

  "coaching institute": [
    (name, city, yourName) =>
`Hi,

I found *${name}* while looking at coaching centres in ${city}.

I help institutes get more admission enquiries with a professional website. Are you currently interested in upgrading your online presence?

Just reply with a quick 'Yes' or 'No'.

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up on my last message.

I can help *${name}* get more enrollments from Google with a new website. Are you interested in this?

A simple 'Yes' or 'No' works!

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last one from my side about *${name}*.

Whenever you want to upgrade your website, happy to help. Otherwise, I'll stop messaging here. 🙏

— ${yourName}`,
  ],

  "interior designers": [
    (name, city, yourName) =>
`Hi,

I came across *${name}* while looking at interior designers in ${city}.

I build beautiful portfolio websites to help designers get more clients. Are you currently interested in upgrading your online presence?

Just reply with a quick 'Yes' or 'No'.

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up on my last message.

I can help *${name}* attract more high-value clients from Google. Are you open to discussing this?

A simple 'Yes' or 'No' is perfectly fine!

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last message about *${name}*.

Whenever you want a portfolio website, I'm here. Otherwise, I won't reach out again. 🙏

— ${yourName}`,
  ],

  "real estate": [
    (name, city, yourName) =>
`Hi,

I found *${name}* while looking at real estate agents in ${city}.

I build professional websites to help agents generate more property leads online. Are you interested in upgrading your online presence?

Just reply with a quick 'Yes' or 'No'.

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up on my last message.

I can help *${name}* get more property enquiries directly from Google. Are you open to discussing this?

A simple 'Yes' or 'No' works for me!

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last message from my side about *${name}*.

Whenever you're ready for a website, happy to help. Otherwise, I'll stop messaging here. 🙏

— ${yourName}`,
  ],

};

// Default fallback template
templates["default"] = templates["chartered accountants"];

/**
 * Get the right message for a lead.
 * @param {string} category  - business category from Sheets
 * @param {number} count     - 0 = first message, 1 = follow-up, 2 = final
 * @param {string} name      - business name
 * @param {string} city      - city
 * @param {string} yourName  - your name from .env
 */
function getMessage(category, count, name, city, yourName) {
  const cat = (category || "").toLowerCase().trim();

  let set = templates["default"];
  for (const key of Object.keys(templates)) {
    if (key === "default") continue;
    if (cat.includes(key) || key.includes(cat.split(" ")[0])) {
      set = templates[key];
      break;
    }
  }

  const idx = Math.min(count, set.length - 1);
  return set[idx](name, city, yourName);
}

module.exports = { getMessage };
