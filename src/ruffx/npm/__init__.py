import ruff as r
from ruff.utils.run import run


def install(base):
  """ Calls npm install and bower install, given the base path base.
      :param base: The base path (__file__) of the caller.
  """

  # Paths
  path = lambda *x: r.path(*[base] + list(x))
  bower = path('node_modules', 'bower', 'bin', 'bower')

  # Dependencies
  npm_install = r.build()
  npm_install.run('npm', 'install')
  npm_install.execute()

  # Source packages
  bower_install = r.build()
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
  for path in sources:
    pass
