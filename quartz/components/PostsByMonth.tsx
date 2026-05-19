import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { resolveRelative } from "../util/path"
import { QuartzPluginData } from "../plugins/vfile"
import { byDateAndAlphabetical } from "./PageList"
import style from "./styles/recentNotes.scss"
import { Date as FmtDate, getDate } from "./Date"
import { classNames } from "../util/lang"

interface Options {
  title?: string
  filter: (f: QuartzPluginData) => boolean
}

const defaultOptions: Options = {
  filter: (f) => {
    const slug = f.slug ?? ""
    if (!slug) return false
    if (slug === "index") return false
    if (slug === "posts") return false
    if (slug.startsWith("tags/")) return false
    if (slug.startsWith("_drafts/")) return false
    return Boolean(f.dates)
  },
}

export default ((userOpts?: Partial<Options>) => {
  const PostsByMonth: QuartzComponent = ({
    allFiles,
    fileData,
    displayClass,
    cfg,
  }: QuartzComponentProps) => {
    const opts = { ...defaultOptions, ...userOpts }
    const pages = allFiles.filter(opts.filter).sort(byDateAndAlphabetical(cfg))

    const groups = new Map<string, QuartzPluginData[]>()
    for (const page of pages) {
      const d = getDate(cfg, page)
      if (!d) continue
      const key = `${d.getFullYear()}년 ${d.getMonth() + 1}월`
      if (!groups.has(key)) groups.set(key, [])
      groups.get(key)!.push(page)
    }

    return (
      <div class={classNames(displayClass, "recent-notes")}>
        {opts.title && <h2>{opts.title}</h2>}
        {Array.from(groups.entries()).map(([month, items]) => (
          <section style="margin-bottom: 1.5rem;">
            <h3 style="margin-bottom: 0.5rem;">{month} ({items.length})</h3>
            <ul class="recent-ul">
              {items.map((page) => {
                const title = page.frontmatter?.title ?? "Untitled"
                return (
                  <li class="recent-li">
                    <div class="section">
                      <div class="desc">
                        <h3>
                          <a href={resolveRelative(fileData.slug!, page.slug!)} class="internal">
                            {title}
                          </a>
                        </h3>
                      </div>
                      {page.dates && (
                        <p class="meta">
                          <FmtDate date={getDate(cfg, page)!} locale={cfg.locale} />
                        </p>
                      )}
                    </div>
                  </li>
                )
              })}
            </ul>
          </section>
        ))}
      </div>
    )
  }

  PostsByMonth.css = style
  return PostsByMonth
}) satisfies QuartzComponentConstructor
