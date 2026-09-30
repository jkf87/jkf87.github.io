import { i18n } from "../../i18n"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "../types"

// 번역 문서 3종은 2026-09-30에 이 도메인에서 별도 호스트로 옮겼다.
// 책과 외부 글에 남아 있는 옛 주소(conanssam.com/<저장소명>/...)로 온 사람은 여기서 새 주소로 넘긴다.
// 서버 응답은 404 그대로이므로 검색엔진은 이 도메인의 색인에서 해당 주소를 뺀다.
const MOVED_HOST = "https://jkf87kc.github.io"
const MOVED_DOCS = [
  { prefix: "openclaw-docs-ko", label: "OpenClaw 한국어 문서" },
  { prefix: "claude-code-docs-ko", label: "Claude Code 한국어 문서" },
  { prefix: "hyperframes-docs-ko", label: "HyperFrames 한국어 문서" },
]
const movedScript = `(function(){var p=${JSON.stringify(
  MOVED_DOCS.map((d) => d.prefix),
)};var seg=location.pathname.split("/")[1];if(p.indexOf(seg)!==-1){location.replace(${JSON.stringify(
  MOVED_HOST,
)}+location.pathname+location.search+location.hash)}})();`

const NotFound: QuartzComponent = ({ cfg }: QuartzComponentProps) => {
  // If baseUrl contains a pathname after the domain, use this as the home link
  const url = new URL(`https://${cfg.baseUrl ?? "example.com"}`)
  const baseDir = url.pathname

  return (
    <article class="popover-hint">
      <script dangerouslySetInnerHTML={{ __html: movedScript }} />
      <h1>404</h1>
      <p>{i18n(cfg.locale).pages.error.notFound}</p>
      <p>
        예전 글 상당수를 주제별 정리글로 다시 쓰는 중입니다. 정리가 끝난 글은 이 주소에서 새 글로 자동
        연결됩니다.
      </p>
      <p>
        <a href={`${baseDir}categories`}>카테고리에서 주제별로 찾아보기</a>
      </p>
      <p>
        한국어 번역 문서는 주소를 옮겼습니다:{" "}
        {MOVED_DOCS.map((d, i) => (
          <>
            {i > 0 ? " · " : ""}
            <a href={`${MOVED_HOST}/${d.prefix}/`}>{d.label}</a>
          </>
        ))}
      </p>
      <a href={baseDir}>{i18n(cfg.locale).pages.error.home}</a>
    </article>
  )
}

export default (() => NotFound) satisfies QuartzComponentConstructor
