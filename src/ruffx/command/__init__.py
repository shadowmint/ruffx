import sys


# Global name register
REGISTRY = {}

def register(name, callback):
  """ Register a command line command to a callback to invoke 
      To register a default task you need to bind it to an existing target.
      eg. 
          register('build', build_stuff)
          register('default', 'build')
  """
  REGISTRY[name] = callback


def help():
  """ Display help if asked """
  keys = ['-h', '-l', '--help', '--list', '-?']
  found = False
  for k in keys:
    for s in sys.argv:
      if k == s:
        found = True
        break
  if found:
    print('   usage: {0} [COMMAND]'.format(sys.argv[0]))
    print('commands: {0}'.format(', '.join(filter(lambda x: x != 'default', REGISTRY.keys()))))
    if 'default' in REGISTRY:
      print(' default: {0}'.format(REGISTRY['default']))
  return found

def run():
  """ Run based on arguments """
  if help():
    return
  target = sys.argv[1] if len(sys.argv) > 1 else None
  callback, target, is_default = _get(target)
  if callback is None:
    print('Invalid command. Try one of: {0}'.format(', '.join(REGISTRY.keys())))
  else:
    if is_default:
      print('- Loading default task: {0}'.format(target))
    print('- Executing task: {0}'.format(target))
    callback()


def _get(name):
  """ Get the bound command, if any """
  is_default = False
  if name is None:
    name = 'default'
  if name == 'default':
    is_default = True
    name = REGISTRY['default']
  if name in REGISTRY:
    return REGISTRY[name], name, is_default
  return None, None, False
