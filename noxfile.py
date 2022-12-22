import nox


@nox.session
def flake8(session):
    session.install("flake8")
    session.run("flake8", "easy2use", 'noxfile.py', 'tests')


@nox.session(name='pytest')
def test(session):
    session.install('pytest')
    session.install('-r', 'requirements.txt', '-r', 'test-requirements.txt')
    session.run('pytest', 'tests')
