-- Seed data for Alumni Connect Platform
USE alumni_connect;

-- Insert sample users
INSERT INTO users (email, password_hash, first_name, last_name, role, graduation_year, degree, major, current_company, current_position, location, bio, skills, linkedin_url, is_verified) VALUES
-- Alumni
('john.doe@alumni.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'John', 'Doe', 'alumni', 2018, 'Bachelor of Technology', 'Computer Science', 'Google', 'Senior Software Engineer', 'San Francisco, CA', 'Passionate software engineer with 5+ years of experience in full-stack development. Love mentoring students and sharing knowledge.', '["JavaScript", "Python", "React", "Node.js", "AWS"]', 'https://linkedin.com/in/johndoe', TRUE),

('sarah.wilson@alumni.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'Sarah', 'Wilson', 'alumni', 2017, 'Master of Business Administration', 'Marketing', 'Microsoft', 'Product Manager', 'Seattle, WA', 'Product management professional with expertise in tech products and user experience. Enjoy helping students navigate career transitions.', '["Product Management", "UX Design", "Data Analysis", "Leadership", "Strategy"]', 'https://linkedin.com/in/sarahwilson', TRUE),

('mike.chen@alumni.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'Mike', 'Chen', 'alumni', 2019, 'Bachelor of Science', 'Data Science', 'Netflix', 'Data Scientist', 'Los Angeles, CA', 'Data scientist specializing in machine learning and analytics. Passionate about using data to solve real-world problems.', '["Python", "Machine Learning", "SQL", "Tableau", "Statistics"]', 'https://linkedin.com/in/mikechen', TRUE),

('emily.rodriguez@alumni.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'Emily', 'Rodriguez', 'alumni', 2016, 'Bachelor of Arts', 'Business Administration', 'Goldman Sachs', 'Investment Banker', 'New York, NY', 'Finance professional with expertise in investment banking and financial analysis. Mentor for students interested in finance careers.', '["Financial Analysis", "Investment Banking", "Excel", "Bloomberg", "Risk Management"]', 'https://linkedin.com/in/emilyrodriguez', TRUE),

-- Mentors
('david.kim@mentor.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'David', 'Kim', 'mentor', 2015, 'Master of Science', 'Computer Science', 'Apple', 'Engineering Manager', 'Cupertino, CA', 'Engineering leader with 8+ years of experience. Specialized in mobile development and team management. Love coaching junior developers.', '["iOS Development", "Swift", "Team Leadership", "System Design", "Agile"]', 'https://linkedin.com/in/davidkim', TRUE),

('lisa.patel@mentor.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'Lisa', 'Patel', 'mentor', 2014, 'Master of Business Administration', 'Entrepreneurship', 'Startup Founder', 'CEO', 'Austin, TX', 'Serial entrepreneur and startup mentor. Founded 3 successful companies. Passionate about helping students develop entrepreneurial skills.', '["Entrepreneurship", "Business Strategy", "Fundraising", "Leadership", "Innovation"]', 'https://linkedin.com/in/lisapatel', TRUE),

-- Students
('alex.johnson@student.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'Alex', 'Johnson', 'student', 2024, 'Bachelor of Technology', 'Computer Science', NULL, 'Student', 'Boston, MA', 'Final year computer science student passionate about web development and machine learning. Looking for internship opportunities.', '["Java", "Python", "React", "Git", "Algorithms"]', 'https://linkedin.com/in/alexjohnson', FALSE),

('maria.garcia@student.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'Maria', 'Garcia', 'student', 2025, 'Bachelor of Science', 'Data Science', NULL, 'Student', 'Chicago, IL', 'Third year data science student with interest in healthcare analytics. Seeking mentorship and internship opportunities.', '["Python", "R", "Statistics", "SQL", "Pandas"]', 'https://linkedin.com/in/mariagarcia', FALSE),

('james.brown@student.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'James', 'Brown', 'student', 2024, 'Bachelor of Business Administration', 'Finance', NULL, 'Student', 'Philadelphia, PA', 'Business student specializing in finance. Interested in investment banking and financial consulting careers.', '["Financial Modeling", "Excel", "Accounting", "Economics", "Analysis"]', 'https://linkedin.com/in/jamesbrown', FALSE),

('priya.sharma@student.com', '$2b$12$LQv3c1yqBwEHxv5hSRNQiOJ7lQK9Q8K9Q8K9Q8K9Q8K9Q8K9Q8K9Q', 'Priya', 'Sharma', 'student', 2025, 'Bachelor of Technology', 'Information Technology', NULL, 'Student', 'San Jose, CA', 'IT student with passion for cybersecurity and cloud computing. Looking for guidance on career paths in tech security.', '["Cybersecurity", "Linux", "Networking", "Cloud Computing", "Python"]', 'https://linkedin.com/in/priyasharma', FALSE);

-- Insert job opportunities
INSERT INTO opportunities (title, company, type, description, requirements, location, salary_range, application_deadline, posted_by) VALUES
('Software Engineer Intern', 'Google', 'internship', 'Join our team for a 12-week summer internship program. Work on real projects that impact millions of users worldwide.', 'Currently pursuing CS degree, proficiency in Python/Java, strong problem-solving skills', 'Mountain View, CA', '$8,000-$10,000/month', '2024-03-15', 1),

('Frontend Developer', 'Microsoft', 'job', 'We are looking for a talented Frontend Developer to join our team and help build the next generation of productivity tools.', '2+ years experience with React, TypeScript, modern CSS, experience with Azure', 'Redmond, WA', '$90,000-$120,000', '2024-04-01', 2),

('Data Science Intern', 'Netflix', 'internship', 'Work with our data science team to analyze user behavior and improve recommendation algorithms.', 'Strong background in statistics, Python, machine learning, SQL experience preferred', 'Los Gatos, CA', '$7,500-$9,000/month', '2024-03-20', 3),

('Investment Banking Analyst', 'Goldman Sachs', 'job', 'Join our investment banking division as an analyst. Work on high-profile M&A transactions and IPOs.', 'Finance degree, strong analytical skills, Excel proficiency, ability to work long hours', 'New York, NY', '$100,000-$150,000', '2024-04-15', 4),

('Mobile Developer Intern', 'Apple', 'internship', 'Contribute to iOS app development and learn from industry experts in mobile technology.', 'iOS development experience, Swift programming, understanding of mobile UI/UX principles', 'Cupertino, CA', '$8,500-$10,500/month', '2024-03-10', 5);

-- Insert scholarships
INSERT INTO scholarships (title, organization, amount, description, eligibility_criteria, application_deadline, application_url, posted_by) VALUES
('Tech Excellence Scholarship', 'Google Foundation', 10000.00, 'Supporting underrepresented students in computer science and related fields.', 'Underrepresented minority in tech, GPA 3.5+, demonstrated financial need, pursuing CS degree', '2024-05-01', 'https://google.org/scholarships/tech-excellence', 1),

('Women in STEM Scholarship', 'Microsoft Foundation', 7500.00, 'Empowering women to pursue careers in science, technology, engineering, and mathematics.', 'Female student, STEM major, GPA 3.0+, leadership experience, essay required', '2024-04-20', 'https://microsoft.com/scholarships/women-stem', 2),

('Data Science Innovation Award', 'Netflix Education Fund', 5000.00, 'For students working on innovative data science projects with real-world applications.', 'Data Science major, original research project, faculty recommendation, portfolio submission', '2024-06-15', 'https://netflix.com/education/data-science-award', 3),

('Future Leaders in Finance', 'Goldman Sachs Foundation', 12000.00, 'Supporting the next generation of financial leaders and innovators.', 'Finance/Economics major, GPA 3.7+, leadership roles, career goals essay, interview required', '2024-05-30', 'https://goldmansachs.com/scholarships/future-leaders', 4),

('Entrepreneurship Excellence Grant', 'Startup Accelerator Fund', 8000.00, 'For students with innovative business ideas and entrepreneurial spirit.', 'Business plan submission, prototype/MVP preferred, mentor recommendation, pitch presentation', '2024-07-01', 'https://startupfund.org/entrepreneurship-grant', 6);

-- Insert mentorship programs
INSERT INTO mentorship_programs (mentor_id, title, description, expertise_areas, max_mentees, duration_weeks) VALUES
(1, 'Full-Stack Development Mentorship', 'Comprehensive program covering frontend and backend development, system design, and career guidance.', '["Web Development", "System Design", "Career Growth", "Technical Interviews"]', 3, 16),

(2, 'Product Management Bootcamp', 'Learn product management fundamentals, user research, and strategic thinking.', '["Product Strategy", "User Research", "Data Analysis", "Leadership"]', 4, 12),

(3, 'Data Science Career Path', 'From basics to advanced machine learning, including portfolio building and job search strategies.', '["Machine Learning", "Data Analysis", "Python", "Career Development"]', 2, 20),

(5, 'iOS Development Mastery', 'Master iOS app development from basics to advanced topics including App Store deployment.', '["iOS Development", "Swift", "Mobile UI/UX", "App Store Optimization"]', 3, 14),

(6, 'Startup Founder Journey', 'Learn how to build and scale a startup from idea to funding.', '["Entrepreneurship", "Business Strategy", "Fundraising", "Team Building"]', 2, 24);

-- Insert mentorship sessions
INSERT INTO mentorship_sessions (program_id, mentor_id, mentee_id, title, session_type, status, scheduled_date, duration_minutes) VALUES
(1, 1, 7, 'Resume Review and Career Planning', 'resume_review', 'scheduled', '2024-02-15 14:00:00', 60),
(1, 1, 8, 'Technical Interview Preparation', 'interview_prep', 'completed', '2024-02-10 16:00:00', 90),
(2, 2, 9, 'Product Management Fundamentals', 'career_guidance', 'scheduled', '2024-02-20 10:00:00', 75),
(3, 3, 8, 'Machine Learning Project Review', 'skill_development', 'completed', '2024-02-08 15:30:00', 60),
(4, 5, 10, 'iOS App Development Best Practices', 'skill_development', 'scheduled', '2024-02-18 13:00:00', 90);

-- Insert webinars
INSERT INTO webinars (title, description, host_id, scheduled_date, duration_minutes, max_participants) VALUES
('Breaking into Tech: A Comprehensive Guide', 'Learn about different career paths in technology, required skills, and how to land your first tech job.', 1, '2024-03-01 18:00:00', 90, 200),

('Product Management 101: From Idea to Launch', 'Understand the product development lifecycle and the role of a product manager in bringing ideas to market.', 2, '2024-03-08 19:00:00', 75, 150),

('Data Science in Practice: Real-world Applications', 'Explore how data science is applied in different industries with case studies and practical examples.', 3, '2024-03-15 17:00:00', 60, 100),

('Entrepreneurship: Building Your First Startup', 'Learn the fundamentals of starting a business, from ideation to funding and scaling.', 6, '2024-03-22 18:30:00', 120, 250);

-- Insert success stories
INSERT INTO success_stories (author_id, title, content, category, tags, is_featured, likes_count, views_count) VALUES
(1, 'From Student to Google: My Journey', 'When I graduated in 2018, I never imagined I would be working at Google today. It all started with a simple internship application and a lot of preparation. Here''s how I made it happen and what I learned along the way...', 'job_placement', '["Google", "Software Engineering", "Career Growth", "Interview Tips"]', TRUE, 45, 1250),

(2, 'How I Transitioned from Engineering to Product Management', 'Making a career pivot can be scary, but with the right approach and mentorship, it''s absolutely possible. Here''s my story of transitioning from a software engineer to a product manager at Microsoft...', 'career_change', '["Career Transition", "Product Management", "Microsoft", "Professional Growth"]', TRUE, 32, 890),

(3, 'Landing a Data Science Role at Netflix', 'The data science field is competitive, but with the right skills and portfolio, you can stand out. Here''s how I prepared for and landed my dream job at Netflix...', 'job_placement', '["Data Science", "Netflix", "Portfolio", "Machine Learning"]', FALSE, 28, 675),

(7, 'My Internship Experience at a Fortune 500 Company', 'As a current student, I want to share my recent internship experience and the valuable lessons I learned. This experience has shaped my career goals and given me confidence for the future...', 'skill_development', '["Internship", "Student Experience", "Professional Development", "Networking"]', FALSE, 15, 420);

-- Insert some applications
INSERT INTO applications (user_id, opportunity_id, application_type, status, cover_letter, submitted_at) VALUES
(7, 1, 'opportunity', 'submitted', 'I am excited to apply for the Software Engineer Intern position at Google. My experience with Python and Java, combined with my passion for solving complex problems, makes me a great fit for this role.', '2024-02-01 10:30:00'),

(8, 3, 'opportunity', 'under_review', 'As a data science student with hands-on experience in machine learning projects, I am thrilled to apply for the Data Science Intern position at Netflix. I believe my analytical skills and creativity would contribute to your recommendation algorithms.', '2024-02-03 14:15:00'),

(9, 4, 'opportunity', 'shortlisted', 'I am writing to express my strong interest in the Investment Banking Analyst position at Goldman Sachs. My finance background and analytical skills, combined with my drive for excellence, align perfectly with your requirements.', '2024-02-05 09:45:00'),

(10, 5, 'opportunity', 'submitted', 'I am passionate about mobile development and would love to contribute to Apple''s innovative iOS applications. My experience with Swift and understanding of mobile UI/UX principles make me an ideal candidate for this internship.', '2024-02-07 16:20:00');

-- Insert scholarship applications
INSERT INTO applications (user_id, scholarship_id, application_type, status, cover_letter, submitted_at) VALUES
(7, 1, 'scholarship', 'submitted', 'As an underrepresented minority in tech with a strong academic record and financial need, I believe the Tech Excellence Scholarship would help me achieve my goals in computer science.', '2024-02-02 11:00:00'),

(8, 2, 'scholarship', 'under_review', 'As a woman pursuing data science, I am committed to breaking barriers in STEM. This scholarship would support my educational journey and help me become a role model for other women in tech.', '2024-02-04 13:30:00'),

(10, 3, 'scholarship', 'submitted', 'My innovative data science project on predictive healthcare analytics demonstrates my commitment to using technology for social good. I would be honored to receive this award to further my research.', '2024-02-06 15:45:00');

-- Insert some connections
INSERT INTO connections (requester_id, recipient_id, status, message, created_at) VALUES
(7, 1, 'accepted', 'Hi John, I''m a CS student interested in learning more about your journey to Google. Would love to connect!', '2024-01-15 10:00:00'),
(8, 3, 'accepted', 'Hello Mike, I''m fascinated by your work in data science at Netflix. Could we connect to discuss career opportunities?', '2024-01-20 14:30:00'),
(9, 4, 'pending', 'Hi Emily, I''m a finance student interested in investment banking. Would appreciate connecting with you for career advice.', '2024-02-01 09:15:00'),
(10, 5, 'accepted', 'Hello David, I''m an IT student passionate about iOS development. Would love to learn from your experience at Apple.', '2024-01-25 16:45:00');

-- Insert some messages
INSERT INTO messages (sender_id, recipient_id, subject, content, sent_at) VALUES
(1, 7, 'Re: Career Advice', 'Hi Alex, thanks for connecting! I''d be happy to share my experience and provide some career guidance. When would be a good time for a quick call?', '2024-01-16 11:30:00'),
(3, 8, 'Data Science Opportunities', 'Hi Maria, I saw your interest in healthcare analytics. We actually have some interesting projects in that area. Let''s schedule a time to discuss!', '2024-01-21 10:15:00'),
(5, 10, 'iOS Development Resources', 'Hi Priya, here are some great resources for learning iOS development that I mentioned. Feel free to reach out if you have any questions!', '2024-01-26 14:20:00');

-- Insert some notifications
INSERT INTO notifications (user_id, type, title, content, related_id, created_at) VALUES
(7, 'application_update', 'Application Status Update', 'Your application for Software Engineer Intern at Google is now under review.', 1, '2024-02-02 09:00:00'),
(8, 'mentorship_request', 'New Mentorship Session Scheduled', 'Your mentorship session with Mike Chen has been scheduled for February 8th at 3:30 PM.', 4, '2024-02-05 16:30:00'),
(9, 'message_received', 'New Message', 'You have received a new message from Emily Rodriguez.', NULL, '2024-02-01 10:00:00'),
(10, 'webinar_reminder', 'Webinar Reminder', 'Don''t forget about the "Breaking into Tech" webinar tomorrow at 6:00 PM.', 1, '2024-02-28 18:00:00');

-- Insert story likes
INSERT INTO story_likes (story_id, user_id, created_at) VALUES
(1, 7, '2024-01-20 10:30:00'),
(1, 8, '2024-01-20 14:15:00'),
(1, 9, '2024-01-21 09:45:00'),
(2, 7, '2024-01-22 11:20:00'),
(2, 10, '2024-01-22 16:30:00'),
(3, 8, '2024-01-23 13:10:00'),
(4, 1, '2024-01-24 15:45:00');