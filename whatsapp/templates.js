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

I help CA firms get a professional website that brings in new clients from Google.

Would you be open to a quick 10-minute call this week?

— ${yourName}`,

    // Day 4 follow-up
    (name, city, yourName) =>
`Hi again,

Just following up on my last message about *${name}*'s website.

Most CA firms in ${city} losing clients online simply don't have a fast, professional website.

I can fix that in 7 days for ₹8,000. Interested?

— ${yourName}`,

    // Day 8 final
    (name, city, yourName) =>
`Hi,

Last message from my side — I don't want to bother you!

If *${name}* ever needs a website, I'm here. ₹8,000, 7 days.

Happy to share examples anytime 🙏

— ${yourName}`,
  ],

  "restaurants": [
    (name, city, yourName) =>
`Hi,

I noticed *${name}* doesn't have a website yet.

Customers in ${city} search on Google before deciding where to eat. A good website means more tables filled.

Can I show you some examples? Takes 10 minutes.

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up about *${name}*'s online presence.

A website with your menu and photos costs ₹8,000 and takes one week. It pays for itself with 2-3 extra tables per week.

Interested?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last follow-up from my side.

If *${name}* ever needs a website, do reach out. ₹8,000, 7 days 🙏

— ${yourName}`,
  ],

  "clinics": [
    (name, city, yourName) =>
`Hi,

I came across *${name}* while looking for clinics in ${city}.

Patients search for doctors on Google before booking. A clean website with your services and timings helps them find and choose you.

Would you like to see how it works? Quick 10-min call?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up about *${name}*'s website.

A professional clinic website helps patients find you on Google and book directly. ₹8,000, ready in 7 days.

Interested to know more?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last message from me about *${name}*.

Whenever you're ready for a website, I'm here. ₹8,000, 7 days 🙏

— ${yourName}`,
  ],

  "coaching institute": [
    (name, city, yourName) =>
`Hi,

I found *${name}* while looking at coaching centres in ${city}.

Students and parents search online before choosing a coaching centre. A website with your courses, results and fees gets you more enquiries.

Interested in a quick chat?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up about *${name}*'s online presence.

A well-made website with Google visibility means more admission enquiries. ₹8,000, 7 days.

Can I show you examples?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last one from my side about *${name}*.

Whenever you're ready for a website, happy to help. ₹8,000, 7 days 🙏

— ${yourName}`,
  ],

  "interior designers": [
    (name, city, yourName) =>
`Hi,

I came across *${name}* while looking at interior designers in ${city}.

Your work deserves to be seen online. A portfolio website helps clients find you on Google and see your projects before calling.

Quick 10-min call to show you how?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up about *${name}*'s portfolio website.

A clean portfolio site with your best projects gets you better clients online. ₹8,000, 7 days.

Interested?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last message about *${name}*.

Whenever you want a portfolio website, I'm here. ₹8,000, 7 days 🙏

— ${yourName}`,
  ],

  "real estate": [
    (name, city, yourName) =>
`Hi,

I found *${name}* while looking at real estate agents in ${city}.

Property buyers search agents online before calling. A website with your listings and area expertise brings direct enquiries.

10-min call this week?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Following up about *${name}*'s website.

A professional real estate website means property enquiries directly from Google — no ad spend needed. ₹8,000, 7 days.

Interested?

— ${yourName}`,

    (name, city, yourName) =>
`Hi,

Last message from my side about *${name}*.

Whenever you're ready for a website, happy to help. ₹8,000, 7 days 🙏

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
