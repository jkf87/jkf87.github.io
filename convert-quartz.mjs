import { JSDOM } from "jsdom";
import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

// --- Converter from naver_blog_hacked (inlined) ---
// We'll import the TS converter logic rewritten for Node

const T = {
  p: "font-size:15px;line-height:1.8;color:#333;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  h1: "font-size:26px;font-weight:700;color:#333;line-height:1.5;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  h2: "font-size:21px;font-weight:700;color:#333;line-height:1.5;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  h3: "font-size:18px;font-weight:700;color:#333;line-height:1.5;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  h4: "font-size:17px;font-weight:700;color:#333;line-height:1.6;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  h5: "font-size:15px;font-weight:700;color:#333;line-height:1.6;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  h6: "font-size:13px;font-weight:700;color:#777;line-height:1.6;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  strong: "font-weight:700;",
  em: "font-style:italic;",
  del: "text-decoration:line-through;color:#777;",
  a: "color:#608cba;text-decoration:underline;",
  img: "max-width:100%;height:auto;display:block;margin:0 auto;",
  codeInline: "background:#f4f5f5;color:#333;padding:2px 6px;border-radius:2px;font-family:'Source Code Pro',Consolas,Monaco,monospace;font-size:13px;",
  codeBlockWrap: "background:#f4f5f5;padding:12px 17px;margin:0;font-family:'Source Code Pro',Consolas,Monaco,monospace;font-size:13px;line-height:1.85;color:#000;overflow-x:auto;",
  codeLine: "white-space:pre;",
  blockquoteWrap: "border-left:6px solid #515151;padding:10px 20px;margin:0;",
  blockquoteP: "font-size:19px;line-height:1.8;color:#333;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  hr: "border:none;height:1px;background:#ddd;margin:0;",
  tableWrap: "overflow-x:auto;",
  table: "border-collapse:separate;width:100%;font-size:15px;border:solid #d2d2d2;border-width:1px 0 0 1px;",
  thead: "",
  tbody: "",
  tr: "",
  th: "border:solid #d2d2d2;border-width:0 1px 1px 0;padding:10px;background:#f7f7f7;font-weight:700;text-align:left;color:#333;",
  td: "border:solid #d2d2d2;border-width:0 1px 1px 0;padding:10px;color:#333;",
  listItem: "font-size:15px;line-height:1.8;color:#333;margin:0;font-family:'Nanum Gothic','나눔고딕',sans-serif;",
  bullet1: "•",
  bullet2: "◦",
  bullet3: "▪",
};

const SPACER = `<p style="font-size:8px;line-height:1;margin:0;">&nbsp;</p>`;
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const NBSP = "&nbsp;";
const indent = (depth) => NBSP.repeat(Math.max(0, depth) * 4);

function renderInlineNode(node) {
  if (node.nodeType === 3) return esc(node.textContent || "");
  if (node.nodeType !== 1) return "";
  const tag = node.tagName.toLowerCase();
  const kids = Array.from(node.childNodes).map(renderInlineNode).join("");

  switch (tag) {
    case "strong": case "b": return `<strong style="${T.strong}">${kids}</strong>`;
    case "em": case "i": return `<em style="${T.em}">${kids}</em>`;
    case "del": case "s": case "strike": return `<del style="${T.del}">${kids}</del>`;
    case "code": return `<code style="${T.codeInline}">${kids}</code>`;
    case "a": {
      const href = node.getAttribute("href") || "#";
      return `<a href="${esc(href)}" style="${T.a}">${kids}</a>`;
    }
    case "br": return "<br/>";
    case "img": {
      const src = node.getAttribute("src") || "";
      const alt = node.getAttribute("alt") || "";
      return `<img src="${esc(src)}" alt="${esc(alt)}" style="${T.img}" />`;
    }
    case "span": case "font": return kids;
    case "u": return `<u>${kids}</u>`;
    default: return kids;
  }
}

function flattenList(ul, depth, ordered, parts) {
  const items = Array.from(ul.children).filter(c => c.tagName.toLowerCase() === "li");
  let n = 1;
  for (const li of items) {
    const nestedLists = [];
    const inlineKids = [];
    for (const child of Array.from(li.childNodes)) {
      if (child.nodeType === 1 && /^(ul|ol)$/i.test(child.tagName)) {
        nestedLists.push(child);
      } else {
        inlineKids.push(child);
      }
    }
    const text = inlineKids.map(renderInlineNode).join("").trim();
    const marker = ordered ? `${n}.` : depth === 0 ? T.bullet1 : depth === 1 ? T.bullet2 : T.bullet3;
    if (text) parts.push(`<p style="${T.listItem}">${indent(depth)}${marker} ${text}</p>`);
    for (const nl of nestedLists) {
      flattenList(nl, depth + 1, nl.tagName.toLowerCase() === "ol", parts);
    }
    n++;
  }
}

function renderBlockNode(node, out) {
  if (node.nodeType === 3) {
    const txt = (node.textContent || "").trim();
    if (txt) out.push(`<p style="${T.p}">${esc(txt)}</p>`);
    return;
  }
  if (node.nodeType !== 1) return;
  const tag = node.tagName.toLowerCase();
  const pushSpacer = () => { if (out.length > 0) out.push(SPACER); };

  switch (tag) {
    case "h1": case "h2": case "h3": case "h4": case "h5": case "h6": {
      pushSpacer();
      const level = parseInt(tag[1], 10);
      const style = [T.h1, T.h2, T.h3, T.h4, T.h5, T.h6][level - 1];
      const inner = Array.from(node.childNodes).map(renderInlineNode).join("");
      out.push(`<h${level} style="${style}">${inner}</h${level}>`);
      return;
    }
    case "p": {
      pushSpacer();
      const inner = Array.from(node.childNodes).map(renderInlineNode).join("");
      if (inner.trim()) out.push(`<p style="${T.p}"><span>${inner}</span></p>`);
      return;
    }
    case "blockquote": {
      pushSpacer();
      const childParts = [];
      for (const c of Array.from(node.childNodes)) {
        if (c.nodeType === 3) {
          const t = (c.textContent || "").trim();
          if (t) childParts.push(`<p style="${T.blockquoteP}">${esc(t)}</p>`);
        } else if (c.nodeType === 1) {
          if (/^p$/i.test(c.tagName)) {
            const inner = Array.from(c.childNodes).map(renderInlineNode).join("");
            childParts.push(`<p style="${T.blockquoteP}">${inner}</p>`);
          } else {
            const inner = renderInlineNode(c);
            if (inner.trim()) childParts.push(`<p style="${T.blockquoteP}">${inner}</p>`);
          }
        }
      }
      out.push(`<div style="${T.blockquoteWrap}">${childParts.join(SPACER)}</div>`);
      return;
    }
    case "pre": {
      pushSpacer();
      const codeEl = node.querySelector("code") || node;
      const text = codeEl.textContent || "";
      const lines = text.replace(/\n$/, "").split("\n").map(l => `<div style="${T.codeLine}">${esc(l) || "&nbsp;"}</div>`).join("");
      out.push(`<div style="${T.codeBlockWrap}">${lines}</div>`);
      return;
    }
    case "hr": {
      pushSpacer();
      out.push(`<hr style="${T.hr}" />`);
      return;
    }
    case "ul": case "ol": {
      pushSpacer();
      const parts = [];
      flattenList(node, 0, tag === "ol", parts);
      out.push(parts.join(""));
      return;
    }
    case "table": {
      pushSpacer();
      const rows = [];
      const theadEl = node.querySelector("thead");
      const tbodyEl = node.querySelector("tbody") || node;
      if (theadEl) {
        const trs = Array.from(theadEl.querySelectorAll("tr"));
        const headCells = trs.flatMap(tr => Array.from(tr.children))
          .map(c => `<th style="${T.th}">${Array.from(c.childNodes).map(renderInlineNode).join("")}</th>`);
        rows.push(`<thead><tr>${headCells.join("")}</tr></thead>`);
      }
      const bodyTrs = Array.from(tbodyEl.querySelectorAll(":scope > tr"));
      const allTrs = bodyTrs.length ? bodyTrs : Array.from(node.querySelectorAll("tr")).filter(tr => !theadEl || !theadEl.contains(tr));
      const bodyRows = allTrs.map(tr => {
        const cells = Array.from(tr.children).map(c => {
          const tagC = c.tagName.toLowerCase();
          const style = tagC === "th" ? T.th : T.td;
          return `<${tagC} style="${style}">${Array.from(c.childNodes).map(renderInlineNode).join("")}</${tagC}>`;
        });
        return `<tr>${cells.join("")}</tr>`;
      });
      rows.push(`<tbody>${bodyRows.join("")}</tbody>`);
      out.push(`<div style="${T.tableWrap}"><table style="${T.table}">${rows.join("")}</table></div>`);
      return;
    }
    case "img": {
      pushSpacer();
      const src = node.getAttribute("src") || "";
      const alt = node.getAttribute("alt") || "";
      out.push(`<p style="margin:0;"><img src="${esc(src)}" alt="${esc(alt)}" style="${T.img}" /></p>`);
      return;
    }
    case "figure": {
      const img = node.querySelector("img");
      if (img) renderBlockNode(img, out);
      const caption = node.querySelector("figcaption");
      if (caption) {
        pushSpacer();
        out.push(`<p style="${T.p};text-align:center;color:#777;font-size:13px;">${Array.from(caption.childNodes).map(renderInlineNode).join("")}</p>`);
      }
      return;
    }
    case "div": case "section": case "article": case "main":
    case "header": case "footer": case "aside": case "nav": {
      for (const c of Array.from(node.childNodes)) renderBlockNode(c, out);
      return;
    }
    case "br": return;
    case "script": case "style": case "link": case "iframe":
    case "embed": case "object": case "noscript": case "meta": return;
    default: {
      const inner = Array.from(node.childNodes).map(renderInlineNode).join("");
      if (inner.trim()) {
        pushSpacer();
        out.push(`<p style="${T.p}"><span>${inner}</span></p>`);
      }
    }
  }
}

// --- Main ---
const htmlContent = readFileSync("quartz_page.html", "utf-8");
const dom = new JSDOM(htmlContent);
const doc = dom.window.document;

// Find article content
const article = doc.querySelector("article");
if (!article) {
  console.error("No article found");
  process.exit(1);
}

// Get title
const firstH1 = article.querySelector("h1") || doc.querySelector("h1");
let title = firstH1 ? firstH1.textContent.trim() : "Untitled";
if (firstH1) firstH1.remove();

// Also remove TOC, callout headers, etc.
const tocEl = article.querySelector(".toc");
if (tocEl) tocEl.remove();

// Remove footnotes section
const footnotes = article.querySelectorAll(".footnotes");
footnotes.forEach(f => f.remove());

// Convert article HTML
const out = [];
for (const c of Array.from(article.childNodes)) {
  renderBlockNode(c, out);
}

const bodyHtml = out.join("");

// Save result
writeFileSync("naver_blog_content.html", bodyHtml, "utf-8");
writeFileSync("naver_blog_title.txt", title, "utf-8");

console.log(`Title: ${title}`);
console.log(`Body HTML length: ${bodyHtml.length}`);
console.log("Saved to naver_blog_content.html");
