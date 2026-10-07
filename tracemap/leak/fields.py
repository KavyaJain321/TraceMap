"""Find email/phone fields and links to pages that probably have forms."""

from __future__ import annotations

FIND_FIELDS_JS = r"""
() => {
  const EMAIL = /e-?mail|ईमेल/i;
  const PHONE = /phone|mobile|\bmob(?:ile|no|_no)?\b|contact.?(?:no|num)|whats.?app|\btel\b|मोबाइल|फ़ोन|फोन/i;
  const BAD = /otp|\bpin\b|pincode|aadha|\bpan\b|card|cvv|account.?n|amount|captcha|search|coupon|password|passwd/i;
  const SKIP = new Set(['hidden','password','submit','button','checkbox','radio','file','image','reset','range','color','date','datetime-local','month','week','time']);
  const out = [];
  let n = 0;
  document.querySelectorAll('input, textarea').forEach((el) => {
    const type = (el.getAttribute('type') || 'text').toLowerCase();
    if (SKIP.has(type) || el.disabled || el.readOnly) return;
    const r = el.getBoundingClientRect();
    const st = getComputedStyle(el);
    if (r.width < 2 || r.height < 2 || st.visibility === 'hidden' || st.display === 'none') return;
    const label = (el.labels && el.labels[0] && el.labels[0].innerText) || '';
    const ac = (el.getAttribute('autocomplete') || '').toLowerCase();
    const desc = [el.name, el.id, el.placeholder, el.getAttribute('aria-label'), ac, label, el.title]
      .filter(Boolean).join(' | ').slice(0, 160);
    if (BAD.test(desc)) return;
    let kind = null;
    if (type === 'email' || ac.includes('email') || EMAIL.test(desc)) kind = 'email';
    else if (type === 'tel' || ac.startsWith('tel') || PHONE.test(desc)) kind = 'phone';
    if (!kind) return;
    el.setAttribute('data-tm-field', String(n));
    out.push({ idx: n, kind: kind, desc: desc || type, type: type });
    n++;
  });
  return out;
}
"""

FORM_LINKS_JS = r"""
() => {
  const RE = /sign.?up|register|regist|subscribe|newsletter|contact|enquir|inquir|get.?in.?touch|request.?a?.?call|callback|apply|get.?started|create.?account|sign.?in|log.?in|my.?account|लॉग|पंजीकरण|संपर्क/i;
  const BAD = /logout|log-out|sign.?out|mailto:|tel:|javascript:/i;
  const seen = new Set();
  const out = [];
  document.querySelectorAll('a[href]').forEach((a) => {
    const text = ((a.innerText || '') + ' ' + (a.getAttribute('aria-label') || '') + ' ' + a.href).slice(0, 300);
    if (!RE.test(text) || BAD.test(text) || seen.has(a.href)) return;
    seen.add(a.href);
    const strong = /sign.?up|register|subscribe|newsletter|contact|enquir/i.test(text) ? 0 : 1;
    out.push({ href: a.href, rank: strong });
  });
  out.sort((x, y) => x.rank - y.rank);
  return out.map((x) => x.href);
}
"""

# Installed in the leak-test context only: makes accidental form submission impossible.
NO_SUBMIT_JS = r"""
(() => {
  document.addEventListener('submit', (e) => { e.preventDefault(); e.stopImmediatePropagation(); }, true);
  try { HTMLFormElement.prototype.submit = function () {}; } catch (e) {}
  try { HTMLFormElement.prototype.requestSubmit = function () {}; } catch (e) {}
})();
"""
