from enum import Enum

BASE_URL_FOR_JIRA_API = "https://api.atlassian.com/ex/jira/{}/"

class JiarScope(str, Enum):
    BASIC = 'offline_access read:me'
    CREATE_PROJECT = 'manage:jira-configuration'

class AssTypeEnum(str, Enum):
    UNASSIGNED = ("UNASSIGNED",)
    PROJECT_LEAD = "PROJECT_LEAD"


class ProjTempKeyEnum(str, Enum):
    GREENHOPPER_BASIC = "com.pyxis.greenhopper.jira:gh-simplified-basic"
    GREENHOPPER_KANBAN = "com.pyxis.greenhopper.jira:gh-simplified-agility-kanban"
    GREENHOPPER_SCRUM = "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum"
    GREENHOPPER_KANBAN_CLASSIC = (
        "com.pyxis.greenhopper.jira:gh-simplified-kanban-classic"
    )
    GREENHOPPER_SCRUM_CLASSIC = "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic"


class ProjTypeKeyEnum(str, Enum):
    SOFTWARE = "software"
