import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import { FileTrieNode } from "./quartz/util/fileTrie"

// Explorer 정렬: 폴더는 가나다순, 파일은 최신 날짜순(내림차순)
const explorerSortFn = (a: FileTrieNode, b: FileTrieNode) => {
  if (a.isFolder && b.isFolder) {
    return a.displayName.localeCompare(b.displayName, undefined, {
      numeric: true,
      sensitivity: "base",
    })
  }
  if (a.isFolder) return -1
  if (b.isFolder) return 1
  const aDates = (a.data as any)?.dates
  const bDates = (b.data as any)?.dates
  const aDate = aDates?.created ?? aDates?.modified ?? aDates?.published
  const bDate = bDates?.created ?? bDates?.modified ?? bDates?.published
  if (aDate && bDate) {
    const at = new Date(aDate).getTime()
    const bt = new Date(bDate).getTime()
    if (bt !== at) return bt - at
  }
  return a.displayName.localeCompare(b.displayName, undefined, {
    numeric: true,
    sensitivity: "base",
  })
}

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [
    Component.ConditionalRender({
      component: Component.RecentNotes({
        title: "최근 글 5개",
        limit: 5,
        linkToMore: "posts" as never,
        showTags: true,
      }),
      condition: (page) => page.fileData.slug === "index",
    }),
    Component.ConditionalRender({
      component: Component.PostsByMonth({}),
      condition: (page) => page.fileData.slug === "posts",
    }),
  ],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/jackyzha0/quartz",
      "Discord Community": "https://discord.gg/cRFFHYye7t",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.Explorer({ sortFn: explorerSortFn }),
  ],
  right: [
    Component.Graph(),
    Component.DesktopOnly(Component.TableOfContents()),
    Component.Backlinks(),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        {
          Component: Component.Search(),
          grow: true,
        },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer({ sortFn: explorerSortFn }),
  ],
  right: [],
}
