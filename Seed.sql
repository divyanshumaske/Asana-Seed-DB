DROP DATABASE IF EXISTS asana;

CREATE DATABASE asana
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE asana;

SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE organizations (
    organization_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL
) ENGINE=InnoDB;

CREATE TABLE users (
    user_id VARCHAR(20) PRIMARY KEY,
    organization_id VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    INDEX idx_users_org (organization_id),
    INDEX idx_users_role (role),
    CONSTRAINT fk_users_org
        FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
) ENGINE=InnoDB;

CREATE TABLE teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL,
    INDEX idx_teams_org (organization_id),
    CONSTRAINT fk_teams_org
        FOREIGN KEY (organization_id) REFERENCES organizations(organization_id)
) ENGINE=InnoDB;

CREATE TABLE team_memberships (
    team_id INT NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    PRIMARY KEY (team_id, user_id),
    CONSTRAINT fk_tm_team
        FOREIGN KEY (team_id) REFERENCES teams(team_id),
    CONSTRAINT fk_tm_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(10) NOT NULL,
    team_id INT NOT NULL,
    owner_id VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    status ENUM('active', 'completed', 'archived') NOT NULL,
    created_at DATETIME NOT NULL,
    INDEX idx_projects_team (team_id),
    INDEX idx_projects_owner (owner_id),
    CONSTRAINT fk_projects_org
        FOREIGN KEY (organization_id) REFERENCES organizations(organization_id),
    CONSTRAINT fk_projects_team
        FOREIGN KEY (team_id) REFERENCES teams(team_id),
    CONSTRAINT fk_projects_owner
        FOREIGN KEY (owner_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

CREATE TABLE sections (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    position INT NOT NULL,
    CONSTRAINT fk_sections_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
) ENGINE=InnoDB;

CREATE TABLE tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    section_id INT,
    parent_task_id INT,
    assignee_id VARCHAR(20),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('todo', 'in_progress', 'blocked', 'done') NOT NULL,
    priority TINYINT CHECK (priority BETWEEN 1 AND 5),
    due_date DATE,
    created_at DATETIME NOT NULL,
    completed_at DATETIME,
    INDEX idx_tasks_project (project_id),
    INDEX idx_tasks_assignee (assignee_id),
    INDEX idx_tasks_parent (parent_task_id),
    CONSTRAINT fk_tasks_project
        FOREIGN KEY (project_id) REFERENCES projects(project_id),
    CONSTRAINT fk_tasks_section
        FOREIGN KEY (section_id) REFERENCES sections(section_id),
    CONSTRAINT fk_tasks_parent
        FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id),
    CONSTRAINT fk_tasks_assignee
        FOREIGN KEY (assignee_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

CREATE TABLE attachments (
    attachment_id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    uploaded_by VARCHAR(20) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    created_at DATETIME NOT NULL,
    CONSTRAINT fk_attachments_task
        FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    CONSTRAINT fk_attachments_user
        FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

SHOW TABLES;
