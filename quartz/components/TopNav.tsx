import { QuartzComponent, QuartzComponentConstructor } from "./types"

const links = [
  { href: "/", label: "홈" },
  { href: "/posts", label: "전체 글" },
  { href: "/categories", label: "카테고리" },
  { href: "/about", label: "소개" },
  { href: "/contact", label: "연락처" },
  { href: "/privacy-policy", label: "개인정보처리방침" },
]

const TopNav: QuartzComponent = ({ displayClass }) => {
  return (
    <nav class={`top-nav ${displayClass ?? ""}`} aria-label="주요 메뉴">
      {links.map((link) => (
        <a href={link.href}>{link.label}</a>
      ))}
    </nav>
  )
}

TopNav.css = `
.top-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem 0.75rem;
  align-items: center;
  margin: 0.75rem 0 1.5rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--lightgray);
}

.top-nav a {
  color: var(--darkgray);
  font-size: 0.92rem;
  text-decoration: none;
  border: 1px solid var(--lightgray);
  border-radius: 999px;
  padding: 0.25rem 0.65rem;
  transition: color 0.15s ease, border-color 0.15s ease, background-color 0.15s ease;
}

.top-nav a:hover {
  color: var(--secondary);
  border-color: var(--secondary);
  background-color: var(--highlight);
}
`

export default (() => TopNav) satisfies QuartzComponentConstructor
