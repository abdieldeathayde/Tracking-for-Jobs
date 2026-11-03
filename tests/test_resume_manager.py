import pytest

from jobapply.resume import resume_manager
from jobapply.resume.resume_manager import ResumeManager


@pytest.fixture
def resume_paths(tmp_path, monkeypatch):
    infra_path = tmp_path / "infra.pdf"
    dev_path = tmp_path / "dev.pdf"
    infra_path.touch()
    dev_path.touch()

    monkeypatch.setattr(
        resume_manager,
        "CV_INFRA_PATH",
        infra_path
    )
    monkeypatch.setattr(
        resume_manager,
        "CV_DEV_PATH",
        dev_path
    )

    return infra_path, dev_path


@pytest.mark.parametrize(
    "title",
    [
        "Analista de Infraestrutura",
        "Suporte Técnico",
        "Especialista em Cibersegurança",
        "Analista de Segurança da Informação",
        "Cybersecurity Analyst",
        "Analista SOC",
    ],
)
def test_selects_infrastructure_resume_for_infrastructure_roles(
    title,
    resume_paths
):
    infra_path, _ = resume_paths

    assert ResumeManager.select(title) == infra_path


@pytest.mark.parametrize(
    "title",
    [
        "Desenvolvedor Java",
        "Programador Python",
        "Engenheiro de Software",
        "Desenvolvedor de Aplicações",
    ],
)
def test_selects_development_resume_for_programming_roles(
    title,
    resume_paths
):
    _, dev_path = resume_paths

    assert ResumeManager.select(title) == dev_path


def test_explicit_area_overrides_title(resume_paths):
    infra_path, _ = resume_paths

    assert ResumeManager.select(
        "Desenvolvedor Java",
        area="infra"
    ) == infra_path


def test_unknown_role_requires_area(resume_paths):
    with pytest.raises(ValueError, match="Não foi possível identificar"):
        ResumeManager.select("Assistente Administrativo")
