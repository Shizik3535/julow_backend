# --- Project AR ---
from app.context.project.application.commands.create_project import CreateProjectCommand, CreateProjectHandler
from app.context.project.application.commands.update_project_info import UpdateProjectInfoCommand, UpdateProjectInfoHandler
from app.context.project.application.commands.archive_project import ArchiveProjectCommand, ArchiveProjectHandler
from app.context.project.application.commands.restore_project import RestoreProjectCommand, RestoreProjectHandler
from app.context.project.application.commands.suspend_project import SuspendProjectCommand, SuspendProjectHandler
from app.context.project.application.commands.reactivate_project import ReactivateProjectCommand, ReactivateProjectHandler
from app.context.project.application.commands.request_project_deletion import (
    RequestProjectDeletionCommand,
    RequestProjectDeletionHandler,
)
from app.context.project.application.commands.change_project_methodology import (
    ChangeProjectMethodologyCommand,
    ChangeProjectMethodologyHandler,
)
from app.context.project.application.commands.change_project_visibility import (
    ChangeProjectVisibilityCommand,
    ChangeProjectVisibilityHandler,
)
from app.context.project.application.commands.transfer_project_ownership import (
    TransferProjectOwnershipCommand,
    TransferProjectOwnershipHandler,
)
from app.context.project.application.commands.add_project_owner import AddProjectOwnerCommand, AddProjectOwnerHandler
from app.context.project.application.commands.remove_project_owner import RemoveProjectOwnerCommand, RemoveProjectOwnerHandler
from app.context.project.application.commands.add_project_custom_field import (
    AddProjectCustomFieldCommand,
    AddProjectCustomFieldHandler,
)
from app.context.project.application.commands.update_project_custom_field import (
    UpdateProjectCustomFieldCommand,
    UpdateProjectCustomFieldHandler,
)
from app.context.project.application.commands.remove_project_custom_field import (
    RemoveProjectCustomFieldCommand,
    RemoveProjectCustomFieldHandler,
)
from app.context.project.application.commands.add_project_milestone import AddProjectMilestoneCommand, AddProjectMilestoneHandler
from app.context.project.application.commands.update_project_milestone import (
    UpdateProjectMilestoneCommand,
    UpdateProjectMilestoneHandler,
)
from app.context.project.application.commands.change_project_milestone_status import (
    ChangeProjectMilestoneStatusCommand,
    ChangeProjectMilestoneStatusHandler,
)

# --- ProjectMembership AR ---
from app.context.project.application.commands.add_project_member import AddProjectMemberCommand, AddProjectMemberHandler
from app.context.project.application.commands.remove_project_member import RemoveProjectMemberCommand, RemoveProjectMemberHandler
from app.context.project.application.commands.deactivate_project_member import (
    DeactivateProjectMemberCommand,
    DeactivateProjectMemberHandler,
)
from app.context.project.application.commands.reactivate_project_member import (
    ReactivateProjectMemberCommand,
    ReactivateProjectMemberHandler,
)
from app.context.project.application.commands.change_project_member_role import (
    ChangeProjectMemberRoleCommand,
    ChangeProjectMemberRoleHandler,
)

# --- Board AR ---
from app.context.project.application.commands.add_board_column import AddBoardColumnCommand, AddBoardColumnHandler
from app.context.project.application.commands.remove_board_column import RemoveBoardColumnCommand, RemoveBoardColumnHandler
from app.context.project.application.commands.reorder_board_columns import ReorderBoardColumnsCommand, ReorderBoardColumnsHandler
from app.context.project.application.commands.change_board_column_wip_limit import (
    ChangeBoardColumnWipLimitCommand,
    ChangeBoardColumnWipLimitHandler,
)
from app.context.project.application.commands.add_board_swimlane import AddBoardSwimlaneCommand, AddBoardSwimlaneHandler
from app.context.project.application.commands.remove_board_swimlane import RemoveBoardSwimlaneCommand, RemoveBoardSwimlaneHandler
from app.context.project.application.commands.add_workflow_status import AddWorkflowStatusCommand, AddWorkflowStatusHandler
from app.context.project.application.commands.remove_workflow_status import (
    RemoveWorkflowStatusCommand,
    RemoveWorkflowStatusHandler,
)
from app.context.project.application.commands.add_workflow_transition import (
    AddWorkflowTransitionCommand,
    AddWorkflowTransitionHandler,
)
from app.context.project.application.commands.remove_workflow_transition import (
    RemoveWorkflowTransitionCommand,
    RemoveWorkflowTransitionHandler,
)
from app.context.project.application.commands.create_project_view import CreateProjectViewCommand, CreateProjectViewHandler
from app.context.project.application.commands.update_project_view import UpdateProjectViewCommand, UpdateProjectViewHandler
from app.context.project.application.commands.delete_project_view import DeleteProjectViewCommand, DeleteProjectViewHandler
from app.context.project.application.commands.add_automation_rule import AddAutomationRuleCommand, AddAutomationRuleHandler
from app.context.project.application.commands.update_automation_rule import (
    UpdateAutomationRuleCommand,
    UpdateAutomationRuleHandler,
)
from app.context.project.application.commands.remove_automation_rule import (
    RemoveAutomationRuleCommand,
    RemoveAutomationRuleHandler,
)

# --- Sprint AR ---
from app.context.project.application.commands.create_sprint import CreateSprintCommand, CreateSprintHandler
from app.context.project.application.commands.start_sprint import StartSprintCommand, StartSprintHandler
from app.context.project.application.commands.complete_sprint import CompleteSprintCommand, CompleteSprintHandler
from app.context.project.application.commands.cancel_sprint import CancelSprintCommand, CancelSprintHandler
from app.context.project.application.commands.update_sprint_goal import UpdateSprintGoalCommand, UpdateSprintGoalHandler
from app.context.project.application.commands.update_sprint_date_range import (
    UpdateSprintDateRangeCommand,
    UpdateSprintDateRangeHandler,
)
from app.context.project.application.commands.create_sprint_retro import CreateSprintRetroCommand, CreateSprintRetroHandler

# --- Epic AR ---
from app.context.project.application.commands.create_epic import CreateEpicCommand, CreateEpicHandler
from app.context.project.application.commands.update_epic import UpdateEpicCommand, UpdateEpicHandler
from app.context.project.application.commands.change_epic_status import ChangeEpicStatusCommand, ChangeEpicStatusHandler

# --- ProjectRole AR ---
from app.context.project.application.commands.create_project_role import CreateProjectRoleCommand, CreateProjectRoleHandler
from app.context.project.application.commands.update_project_role import UpdateProjectRoleCommand, UpdateProjectRoleHandler
from app.context.project.application.commands.delete_project_role import DeleteProjectRoleCommand, DeleteProjectRoleHandler

# --- RetroTemplate AR ---
from app.context.project.application.commands.create_retro_template import (
    CreateRetroTemplateCommand,
    CreateRetroTemplateHandler,
)
from app.context.project.application.commands.update_retro_template import (
    UpdateRetroTemplateCommand,
    UpdateRetroTemplateHandler,
)
from app.context.project.application.commands.delete_retro_template import (
    DeleteRetroTemplateCommand,
    DeleteRetroTemplateHandler,
)

__all__ = [
    # Project AR
    "CreateProjectCommand",
    "CreateProjectHandler",
    "UpdateProjectInfoCommand",
    "UpdateProjectInfoHandler",
    "ArchiveProjectCommand",
    "ArchiveProjectHandler",
    "RestoreProjectCommand",
    "RestoreProjectHandler",
    "SuspendProjectCommand",
    "SuspendProjectHandler",
    "ReactivateProjectCommand",
    "ReactivateProjectHandler",
    "RequestProjectDeletionCommand",
    "RequestProjectDeletionHandler",
    "ChangeProjectMethodologyCommand",
    "ChangeProjectMethodologyHandler",
    "ChangeProjectVisibilityCommand",
    "ChangeProjectVisibilityHandler",
    "TransferProjectOwnershipCommand",
    "TransferProjectOwnershipHandler",
    "AddProjectOwnerCommand",
    "AddProjectOwnerHandler",
    "RemoveProjectOwnerCommand",
    "RemoveProjectOwnerHandler",
    "AddProjectCustomFieldCommand",
    "AddProjectCustomFieldHandler",
    "UpdateProjectCustomFieldCommand",
    "UpdateProjectCustomFieldHandler",
    "RemoveProjectCustomFieldCommand",
    "RemoveProjectCustomFieldHandler",
    "AddProjectMilestoneCommand",
    "AddProjectMilestoneHandler",
    "UpdateProjectMilestoneCommand",
    "UpdateProjectMilestoneHandler",
    "ChangeProjectMilestoneStatusCommand",
    "ChangeProjectMilestoneStatusHandler",
    # ProjectMembership AR
    "AddProjectMemberCommand",
    "AddProjectMemberHandler",
    "RemoveProjectMemberCommand",
    "RemoveProjectMemberHandler",
    "DeactivateProjectMemberCommand",
    "DeactivateProjectMemberHandler",
    "ReactivateProjectMemberCommand",
    "ReactivateProjectMemberHandler",
    "ChangeProjectMemberRoleCommand",
    "ChangeProjectMemberRoleHandler",
    # Board AR
    "AddBoardColumnCommand",
    "AddBoardColumnHandler",
    "RemoveBoardColumnCommand",
    "RemoveBoardColumnHandler",
    "ReorderBoardColumnsCommand",
    "ReorderBoardColumnsHandler",
    "ChangeBoardColumnWipLimitCommand",
    "ChangeBoardColumnWipLimitHandler",
    "AddBoardSwimlaneCommand",
    "AddBoardSwimlaneHandler",
    "RemoveBoardSwimlaneCommand",
    "RemoveBoardSwimlaneHandler",
    "AddWorkflowStatusCommand",
    "AddWorkflowStatusHandler",
    "RemoveWorkflowStatusCommand",
    "RemoveWorkflowStatusHandler",
    "AddWorkflowTransitionCommand",
    "AddWorkflowTransitionHandler",
    "RemoveWorkflowTransitionCommand",
    "RemoveWorkflowTransitionHandler",
    "CreateProjectViewCommand",
    "CreateProjectViewHandler",
    "UpdateProjectViewCommand",
    "UpdateProjectViewHandler",
    "DeleteProjectViewCommand",
    "DeleteProjectViewHandler",
    "AddAutomationRuleCommand",
    "AddAutomationRuleHandler",
    "UpdateAutomationRuleCommand",
    "UpdateAutomationRuleHandler",
    "RemoveAutomationRuleCommand",
    "RemoveAutomationRuleHandler",
    # Sprint AR
    "CreateSprintCommand",
    "CreateSprintHandler",
    "StartSprintCommand",
    "StartSprintHandler",
    "CompleteSprintCommand",
    "CompleteSprintHandler",
    "CancelSprintCommand",
    "CancelSprintHandler",
    "UpdateSprintGoalCommand",
    "UpdateSprintGoalHandler",
    "UpdateSprintDateRangeCommand",
    "UpdateSprintDateRangeHandler",
    "CreateSprintRetroCommand",
    "CreateSprintRetroHandler",
    # Epic AR
    "CreateEpicCommand",
    "CreateEpicHandler",
    "UpdateEpicCommand",
    "UpdateEpicHandler",
    "ChangeEpicStatusCommand",
    "ChangeEpicStatusHandler",
    # ProjectRole AR
    "CreateProjectRoleCommand",
    "CreateProjectRoleHandler",
    "UpdateProjectRoleCommand",
    "UpdateProjectRoleHandler",
    "DeleteProjectRoleCommand",
    "DeleteProjectRoleHandler",
    # RetroTemplate AR
    "CreateRetroTemplateCommand",
    "CreateRetroTemplateHandler",
    "UpdateRetroTemplateCommand",
    "UpdateRetroTemplateHandler",
    "DeleteRetroTemplateCommand",
    "DeleteRetroTemplateHandler",
]
