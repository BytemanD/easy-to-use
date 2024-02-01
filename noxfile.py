import nox


@nox.session
def flake8(session: nox.Session):
    session.install("flake8")
    session.run("flake8", "easy2use", 'noxfile.py', 'tests')


@nox.session(name='pytest')
def test(session: nox.Session):
    session.install('-r', 'requirements.txt', '-r', 'test-requirements.txt')
    session.run('pytest', 'tests', *session.posargs)
