import { FilePath, QUARTZ, joinSegments } from "../../util/path"
import { QuartzEmitterPlugin } from "../types"
import fs from "fs"
import { glob } from "../../util/glob"
import { dirname } from "path"

interface Options {
  /** Static files that must also be emitted at the site root. */
  rootFiles: string[]
}

export const Static: QuartzEmitterPlugin<Partial<Options>> = (userOpts) => ({
  name: "Static",
  async *emit({ argv, cfg }) {
    const opts: Options = { rootFiles: [], ...userOpts }
    const staticPath = joinSegments(QUARTZ, "static")
    const fps = await glob("**", staticPath, cfg.configuration.ignorePatterns)
    const outputStaticPath = joinSegments(argv.output, "static")
    await fs.promises.mkdir(outputStaticPath, { recursive: true })
    for (const fp of fps) {
      const src = joinSegments(staticPath, fp) as FilePath
      const dest = joinSegments(outputStaticPath, fp) as FilePath
      await fs.promises.mkdir(dirname(dest), { recursive: true })
      await fs.promises.copyFile(src, dest)
      yield dest
    }

    for (const rootFile of opts.rootFiles) {
      const src = joinSegments(staticPath, rootFile) as FilePath
      const dest = joinSegments(argv.output, rootFile) as FilePath
      await fs.promises.mkdir(dirname(dest), { recursive: true })
      await fs.promises.copyFile(src, dest)
      yield dest
    }
  },
  async *partialEmit() {},
})
