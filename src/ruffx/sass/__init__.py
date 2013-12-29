from os.path import dirname
import ruff as r
import ruffx


def compile(base, output, source, bind=True):
  """ Returns a build for compiling sass files.

      You might, for example, want to call this from a project root
      multiple times to access submodules:

      ruffx.sass.compile(__file__, ['public_html/css/lib1.css'], ['lib/lib1'])
      ruffx.sass.compile(__file__, ['public_html/css/lib2.css'], ['stylesheets'])

      If bind is set, the result is bound internally; you typically want
      to do this, but some ops (eg. rebuild) may want to run the build.execute()
      manually.

      This module requires that sass is installed and in the system path.
      Typically you'd do that with: gem install sass

      :param base: The base path to work for; __file__ of the caller typically.
      :param output: The output path array for a file to generate.
      :param source: The target to process; a single scss file, typically.
      :return: A Build object for the given sources.
  """

  # Paths
  path = lambda *x: r.path(*[base] + list(x))
  output_path = path(*output)
  source_path = path(*source)

  # Build
  build = r.build().run('sass', source_path, output_path)

  # Target
  target = r.target(timeout=10)
  target.pattern('.*\.scss$', dirname(source_path), recurse=True)

  # Bind if required
  if bind:
    r.bind(target, build)

  # Run?
  if ruffx.BUILD:
    build.execute()

  return build
