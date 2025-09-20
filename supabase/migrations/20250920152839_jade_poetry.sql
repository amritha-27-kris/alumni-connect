-- Alumni Connect & Scholarship Support Platform Database Schema
-- MySQL Database Schema

DROP DATABASE IF EXISTS alumni_connect;
CREATE DATABASE alumni_connect;
USE alumni_connect;

-- Users table with enhanced profile information
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role ENUM('student', 'alumni', 'mentor', 'admin') NOT NULL DEFAULT 'student',
    graduation_year INT,
    degree VARCHAR(100),
    major VARCHAR(100),
    current_company VARCHAR(100),
    current_position VARCHAR(100),
    location VARCHAR(100),
    bio TEXT,
    skills TEXT, -- JSON array of skills
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    profile_image VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Job and internship opportunities
CREATE TABLE opportunities (
    opportunity_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    company VARCHAR(100) NOT NULL,
    type ENUM('job', 'internship') NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(100),
    salary_range VARCHAR(50),
    application_deadline DATE,
    posted_by INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (posted_by) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Scholarship opportunities
CREATE TABLE scholarships (
    scholarship_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    organization VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2),
    description TEXT NOT NULL,
    eligibility_criteria TEXT NOT NULL,
    application_deadline DATE NOT NULL,
    application_url VARCHAR(255),
    posted_by INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (posted_by) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Mentorship programs and sessions
CREATE TABLE mentorship_programs (
    program_id INT PRIMARY KEY AUTO_INCREMENT,
    mentor_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    expertise_areas TEXT, -- JSON array
    max_mentees INT DEFAULT 5,
    duration_weeks INT DEFAULT 12,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mentor_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Individual mentorship sessions
CREATE TABLE mentorship_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    program_id INT,
    mentor_id INT NOT NULL,
    mentee_id INT NOT NULL,
    title VARCHAR(200),
    description TEXT,
    session_type ENUM('resume_review', 'interview_prep', 'career_guidance', 'skill_development', 'networking') NOT NULL,
    status ENUM('requested', 'scheduled', 'completed', 'cancelled') DEFAULT 'requested',
    scheduled_date DATETIME,
    duration_minutes INT DEFAULT 60,
    meeting_link VARCHAR(255),
    notes TEXT,
    feedback_rating INT CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    feedback_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (program_id) REFERENCES mentorship_programs(program_id) ON DELETE SET NULL,
    FOREIGN KEY (mentor_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (mentee_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Webinars and events
CREATE TABLE webinars (
    webinar_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    host_id INT NOT NULL,
    scheduled_date DATETIME NOT NULL,
    duration_minutes INT DEFAULT 90,
    max_participants INT DEFAULT 100,
    meeting_link VARCHAR(255),
    registration_required BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Webinar registrations
CREATE TABLE webinar_registrations (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    webinar_id INT NOT NULL,
    user_id INT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attended BOOLEAN DEFAULT FALSE,
    UNIQUE KEY unique_registration (webinar_id, user_id),
    FOREIGN KEY (webinar_id) REFERENCES webinars(webinar_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Success stories
CREATE TABLE success_stories (
    story_id INT PRIMARY KEY AUTO_INCREMENT,
    author_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category ENUM('job_placement', 'scholarship', 'career_change', 'skill_development', 'networking') NOT NULL,
    tags TEXT, -- JSON array
    is_featured BOOLEAN DEFAULT FALSE,
    likes_count INT DEFAULT 0,
    views_count INT DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Applications for opportunities and scholarships
CREATE TABLE applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    opportunity_id INT NULL,
    scholarship_id INT NULL,
    application_type ENUM('opportunity', 'scholarship') NOT NULL,
    status ENUM('submitted', 'under_review', 'shortlisted', 'accepted', 'rejected') DEFAULT 'submitted',
    cover_letter TEXT,
    resume_url VARCHAR(255),
    additional_documents TEXT, -- JSON array of document URLs
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(opportunity_id) ON DELETE CASCADE,
    FOREIGN KEY (scholarship_id) REFERENCES scholarships(scholarship_id) ON DELETE CASCADE,
    CHECK ((opportunity_id IS NOT NULL AND scholarship_id IS NULL) OR (opportunity_id IS NULL AND scholarship_id IS NOT NULL))
);

-- Messages between users
CREATE TABLE messages (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    recipient_id INT NOT NULL,
    subject VARCHAR(200),
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Notifications
CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    type ENUM('application_update', 'mentorship_request', 'webinar_reminder', 'message_received', 'story_featured') NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_id INT, -- ID of related entity (application, session, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- User connections (networking)
CREATE TABLE connections (
    connection_id INT PRIMARY KEY AUTO_INCREMENT,
    requester_id INT NOT NULL,
    recipient_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'declined') DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_connection (requester_id, recipient_id),
    FOREIGN KEY (requester_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CHECK (requester_id != recipient_id)
);

-- Story likes
CREATE TABLE story_likes (
    like_id INT PRIMARY KEY AUTO_INCREMENT,
    story_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_like (story_id, user_id),
    FOREIGN KEY (story_id) REFERENCES success_stories(story_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_graduation_year ON users(graduation_year);
CREATE INDEX idx_opportunities_type ON opportunities(type);
CREATE INDEX idx_opportunities_posted_by ON opportunities(posted_by);
CREATE INDEX idx_scholarships_deadline ON scholarships(application_deadline);
CREATE INDEX idx_mentorship_sessions_mentor ON mentorship_sessions(mentor_id);
CREATE INDEX idx_mentorship_sessions_mentee ON mentorship_sessions(mentee_id);
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_messages_recipient ON messages(recipient_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_connections_status ON connections(status);