import os
import ruff as r
from ruff.utils.run import run
from ruff.os import Color


def install(base):
  """ Calls npm install and bower install, given the base path base.
      :param base: The base path (__file__) of the caller.
  """

  # Paths
  path = lambda *x: r.path(*[base] + list(x))
  bower = path('node_modules', 'bower', 'bin', 'bower')

  # Dependencies
  npm_install = r.build()
  npm_install.notice('npm setup')
  npm_install.run('npm', 'install')
  npm_install.execute()

  # Source packages
  bower_install = r.build()
  bower_install.notice('bower setup')
  bower_install.run('node', bower, 'install')
  bower_install.execute()


def bower_publish(base, target, sources, cache='bower_components'):
  """ Install certain bower files into a specific folder.

      By default the bower install directory is bower_components
      (use cache=... to specify an alternative).

      However, we seldom want to push all of the files in the
      bower install (especially git clones) into the public
      folder.

      This searches the cache folder for files that match the
      given pattern and install then in the target folder.
      It's not really designed to copy entire folders over,
      and it makes no effort to protect files in the target
      folder.

      eg.
      bower_publish(base, ['public', 'libs'], ['jquery.js', 'pixi.js', 'photon.js'])

      :param base: The path base, typically __file__ of the caller.
      :param target: The array for the target path.
      :param sources: An array of file targets to find and copy.
      :param cache: The cache folder to search in.
  """
  def runner(*args):
    cpath = os.path.join(os.path.dirname(base), cache)
    target.insert(0, os.path.dirname(base))
    found = []
    for root, dirs, files in os.walk(os.path.join(base, cpath)):
      for file in files:
        for path in sources:
          if path not in found:
            if file.lower() == path.lower():
              source = os.path.join(root, file)
              output = target[:]
              output.append(file)
              output = os.path.join(*target)
              found.append(path)
              print('- {0}Publishing{1}: {2}'.format(Color.GREEN, Color.RESET, source))
              run('cp', source, output)
  build = r.build()
  build.notice('bower publish')
  build.command(runner)
  build.execute()
