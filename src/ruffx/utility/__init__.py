import os
import ruff
from ruff.os import Color


def clean(base, folder, patterns):
  """ Clean up a folder of files matching the given patterns.
      Clean does not do recursive directory removal. That's scary.
      eg. clean(__file__, ['dist'], ['.*\.dll', '.*\.exe'])

      Clean does not watch for build targets (how would that even work? O_o)
      rather it should be added as a dependency on some other build task.
  """
  source_folder = ruff.path(base, *folder)
  def process_files(files, run):
    for path in files:
      print('- {0}Removing file{1}: {2}'.format(Color.GREEN, Color.RESET, path) )
      os.remove(path)

  build = ruff.build()
  build.notice('Clean')
  build.chdir(source_folder)
  for pattern in patterns:
    build.collect(pattern, process_files)

  return build
