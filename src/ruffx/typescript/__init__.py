import os
from os.path import dirname
import ruff as r
import ruffx


def compile(base, output, source, bind=True, skip=False):
    """ Returns a build for compiling typescript files.

        Using the --out directive, typescript will emit a js file with all the
        included references, so just create a base file that performs all the
        required includes.

        A default output file .d.ts is also generated in the output folder.

        You may want to run this multiple times:

        ruffx.typescript.compile(__file__, ['public_html/js/lib1.js'], ['lib/lib1/ts/all.ts'])
        ruffx.typescript.compile(__file__, ['public_html/js/lib2.js'], ['lib/lib2/ts/all.ts'])
        ruffx.typescript.compile(__file__, ['public_html/js/app.js'], ['ts/all.ts'])

        If bind is set, the result is bound internally; you typically want
        to do this, but some ops (eg. rebuild) may want to run the build.execute()
        manually.

        :param base: The base path to work for; __file__ of the caller typically.
        :param output: The output path array for a file to generate.
        :param source: The base .ts file to compile.
        :return: A Build object for the given sources.
    """

    # Paths
    path = lambda *x: r.path(*[base] + list(x))
    tsc_path = path('node_modules', 'typescript', 'bin', 'tsc.js')
    output_path = path(*output)
    source_path = path(*source)
    source_folder = path(*source[:-1])

    # Build
    build = r.build()
    build.notice('Typescript compile')
    build.chdir(source_folder)
    build.run('node', tsc_path, source_path, '--declaration', '--out', output_path)

    # Target
    target = r.target(timeout=10)
    target.pattern('.*\.ts$', dirname(source_path), recurse=True)

    # Bind if required
    if bind:
        r.bind(target, build)

    # Run?
    if ruffx.BUILD and not skip:
        build.execute()

    return build


def test(base, output, source, bind=True):
    """ Compiles a target, then invokes it using node.
        :param base: The base path to work for; __file__ of the caller typically.
        :param output: The output path array for a file to generate.
        :param source: The base .ts file to compile.
        :return: A Build object for the given sources.
    """

    # Paths
    path = lambda *x: r.path(*[base] + list(x))
    runner = 'node'
    output_path = path(*output)
    source_path = path(*source)
    output_folder = path(*output[:-1])

    # Build
    build = compile(base, output, source, bind=False, skip=True)
    build.notice('Typescript tests')
    build.chdir(output_folder)
    build.run(runner, output_path)

    # Target
    target = r.target(timeout=10)
    target.pattern('.*\.ts$', dirname(source_path), recurse=True)

    # Bind if required
    if bind:
        r.bind(target, build)

    # Run?
    if ruffx.BUILD:
        build.execute()

    return build


def compile_modules(base, output, source, bind=True):
    """ Returns a build for compiling multiple typescript modules
        This works exactly like compile_files with amd = True.

        :param base: The base path to work for; __file__ of the caller typically.
        :param output: The output path array for a directory to generate in.
        :return: A Build object for the given sources.
    """
    return compile_files(base, output, source, bind, amd=True)


def compile_files(base, output, source, bind=True, amd=False):
    """ Returns a build for compiling multiple typescript files.

        Every matching.ts file will be processed separately.

        If bind is set, the result is bound internally; you typically want
        to do this, but some ops (eg. rebuild) may want to run the build.execute()
        manually.

        :param base: The base path to work for; __file__ of the caller typically.
        :param output: The output path array for a directory to generate in.
        :param source: The Folder to walk through.
        :param amd: If true, use amd module compliation.
        :return: A Build object for the given sources.
    """

    # Paths
    path = lambda *x: r.path(*[base] + list(x))
    tsc_path = path('node_modules', 'typescript', 'bin', 'tsc.js')
    output_folder = path(*output)
    source_folder = path(*source)

    # Compile each file. Sometimes --module seems to screw up the use
    # of --out, so safely check and fix if required.
    def collection(matches, run):
        for path in matches:
            output_module_name = os.path.basename(path)[:-3] + '.js'
            generated_file = os.path.join(source_folder, output_module_name)
            required_file = os.path.join(output_folder, output_module_name)
            run('mkdir', '-p', os.path.dirname(required_file))
            if amd:
                run('node', tsc_path, path, '--module', 'amd', '--out', required_file)
            else:
                run('node', tsc_path, path, '--out', required_file)
            if os.path.exists(generated_file):  # wtf?
                run('mv', generated_file, required_file)

    # Build
    build = r.build()
    build.notice('Typescript multifile compile')
    build.chdir(source_folder)
    build.collect('.*\.ts$', collection)

    # Target
    target = r.target(timeout=10)
    target.pattern('.*[^d]\.ts$', dirname(source_folder), recurse=True)

    # Bind if required
    if bind:
        r.bind(target, build)

    # Run?
    if ruffx.BUILD:
        build.execute()

    return build
