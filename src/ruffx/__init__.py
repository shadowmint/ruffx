# Should the ruff extensions run build function immediately?
BUILD = False


def build():
  """ Tell helpers this is a build; execute scripts immediately """
  globals()['BUILD'] = True
