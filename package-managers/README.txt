RELEASES

This is a drop in app that can do:

- Releases to pypi
- Releases to github
- Create apt packages from the pypi release
- Create brew packages from the pypi release

And can be ran both locally and remotely via GitHub Actions.

1. Installation

    1.1 Copy the content of this dir to your project root
    1.2 run the install (to be done: lets install bia brew + script

2. Running

The program to run is the new-release.sh script.

2.1 The new-release.sh script

Execution can be customized :

- Target:
    - default: all (pypi, brew, apt)
    - --publish-to pypi|brew|apt - if one is specified, only that target will be used
- Enviroment:
    - default: github actions
    - --local , defaults to false
- Steps:
    - default: all (build, verify and commit)
    - --build or --verify (includes build and verify)

2.2 The github workflow


Execution can be customized :

The workflow is package-release.yml
It  can only run remotely, on github actions, and does the full steps.

One can customize where to publish to :

The publish-to option can be used to specify where to publish the release to. It can be one of the following:
- pypi
- brew
- apt
