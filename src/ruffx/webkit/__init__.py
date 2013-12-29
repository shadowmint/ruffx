import os
import ruff as r
from ruff.utils.run import run


# Synchronize these urls from: https://github.com/rogerwang/node-webkit
CONFIG_MAC = 'https://s3.amazonaws.com/node-webkit/v0.8.4/node-webkit-v0.8.4-osx-ia32.zip'
CONFIG_WIN = 'https://s3.amazonaws.com/node-webkit/v0.8.4/node-webkit-v0.8.4-win-ia32.zip'


def setup(base, cache_folder):
  """ Downloads the node-webkit build and unzips it in the cache folder.
      This only runs if no already cached version is present.
  """

  # Paths
  path = lambda *x: r.path(*[base] + list(x))
  real_cache_folder = path(*cache_folder)
  real_cache =  cache_folder + ['node_webkit.zip']
  real_cache_target = path(*cache_folder)

  # Download url
  if r.MAC:
    url = CONFIG_MAC
  elif r.WINDOWNS:
    url = CONFIG_WIN
  else:
    raise NotImplementedError('Unsupported OS')

  # Download if missing
  if not os.path.exists(real_cache_target):
    download = r.build()
    download.run('mkdir', '-p', real_cache_folder)
    download.chdir(real_cache_folder)
    download.run('curl', url, '-o', 'node_webkit.zip')
    download.run('unzip', 'node_webkit.zip')
    download.execute()


def distribute(base, source_folder, dist_target, cache_folder, no_dmg=False):
  """ Builds a distributable target
      @param no_dmg Set this for quick testing, it won't package a dmg.
  """

  # Setup
  setup(base, cache_folder)
  path = lambda *x: r.path(*[base] + list(x))

  if r.MAC:

    # Paths
    source = cache_folder + ['node-webkit.app']
    source_app = path(*source)
    target_app = path(*dist_target) + '.app'
    dist_file = path(*dist_target) + '.dmg'
    target_resources = os.path.join(target_app, 'Contents', 'Resources')
    target_dir = os.path.dirname(target_app)
    source_dir = path(*source_folder)
    bundle_target = os.path.join(target_dir, 'app.nw')

    # Cleanup
    if os.path.exists(target_dir):
      cleanup = r.build()
      cleanup.chdir(target_dir)
      if os.path.exists(bundle_target):
        cleanup.run('rm', bundle_target)
      if os.path.exists(dist_file):
        cleanup.run('rm', dist_file)
      if os.path.exists(target_app):
        cleanup.run('rm', '-r', target_app)
      cleanup.execute()

    # Create target
    builder = r.build()
    builder.run('mkdir', '-p', target_dir)
    builder.chdir(target_dir)
    builder.run('cp', '-r', source_app, target_app)
    builder.execute()

    # Create a zip bundle
    bundle = r.build()
    bundle.chdir(source_dir)
    bundle.run('zip', '-r', bundle_target, '.')
    bundle.execute()

    # Finalize by moving app.nw into target
    finalize = r.build()
    finalize.chdir(target_dir)
    finalize.run('cp', bundle_target, target_resources)
    if not no_dmg:
      finalize.run('hdiutil', 'create', dist_file, '-srcfolder', target_app, '-ov')
    finalize.execute()

    # Notice
    print(': Launch: cd {0}; open {1}'.format(target_dir, os.path.basename(target_app)))
    if not no_dmg:
      print(':   Dist: {0}'.format(dist_file))

  else:
    raise NotImplementedError('Unsupported OS')
