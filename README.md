# Alumni Connect & Scholarship Support Platform

A comprehensive platform connecting alumni with current students for career guidance, job opportunities, scholarships, and mentorship. Built as a mini LinkedIn specifically for educational institutions.

## 🎯 Project Overview

This platform addresses the lack of centralized alumni-student interaction by providing:
- **Job & Internship Postings** by alumni
- **Scholarship Opportunities** with eligibility tracking
- **Mentorship Programs** for resume building, interview prep, and skill development
- **Alumni-hosted Webinars** and networking events
- **Success Stories** sharing and inspiration
- **Direct Alumni-Student Communication**

## 🛠 Tech Stack

- **Frontend**: React.js with modern hooks and responsive design
- **Backend**: Flask (Python) with RESTful APIs
- **Database**: MySQL with optimized schema design
- **Authentication**: JWT-based secure authentication
- **Styling**: Modern CSS with responsive design

## 🚀 Features

### For Students:
- Browse job opportunities and internships
- Search and apply for scholarships
- Find mentors based on skills and interests
- Join webinars and networking events
- Share success stories
- Track application status

### For Alumni:
- Post job openings and internships
- Share scholarship opportunities
- Offer mentorship services
- Host webinars and events
- Connect with students
- View engagement analytics

### For Mentors:
- Manage mentorship sessions
- Schedule meetings with students
- Track mentoring progress
- Share expertise and resources

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- npm or yarn

## 🔧 Installation & Setup

### 1. Clone and Setup
```bash
git clone <repository-url>
cd alumni-connect-platform
npm run setup
```

### 2. Database Setup
```bash
# Create MySQL database
mysql -u root -p
CREATE DATABASE alumni_connect;
exit

# Import schema
npm run db:setup
```

### 3. Environment Configuration

Create `.env` files in both client and server directories:

**server/.env:**
```
DATABASE_HOST=localhost
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=alumni_connect
JWT_SECRET=your_jwt_secret_key
FLASK_ENV=development
```

**client/.env:**
```
REACT_APP_API_URL=http://localhost:5000
```

### 4. Install Dependencies

**Backend:**
```bash
cd server
pip install -r requirements.txt
```

**Frontend:**
```bash
cd client
npm install
```

### 5. Run the Application
```bash
# Run both frontend and backend
npm run dev

# Or run separately:
# Backend: npm run server:dev
# Frontend: npm run client:dev
```

## 📁 Project Structure

```
alumni-connect-platform/
├── client/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context for state management
│   │   ├── services/      # API service functions
│   │   ├── utils/         # Utility functions
│   │   └── styles/        # CSS styles
│   ├── package.json
│   └── .env
├── server/                # Flask backend
│   ├── app/
│   │   ├── models/        # Database models
│   │   ├── routes/        # API routes
│   │   ├── utils/         # Utility functions
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── run.py
│   └── .env
├── database/              # Database schema and migrations
│   ├── schema.sql
│   └── seed_data.sql
├── README.md
└── package.json
```

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/alumni` - Get all alumni
- `GET /api/users/students` - Get all students

### Opportunities
- `GET /api/opportunities` - Get all opportunities
- `POST /api/opportunities` - Create new opportunity
- `PUT /api/opportunities/:id` - Update opportunity
- `DELETE /api/opportunities/:id` - Delete opportunity

### Scholarships
- `GET /api/scholarships` - Get all scholarships
- `POST /api/scholarships` - Create scholarship
- `GET /api/scholarships/eligible` - Get eligible scholarships

### Mentorship
- `GET /api/mentorship/sessions` - Get mentorship sessions
- `POST /api/mentorship/request` - Request mentorship
- `PUT /api/mentorship/sessions/:id` - Update session

### Applications
- `POST /api/applications` - Submit application
- `GET /api/applications/my` - Get user's applications
- `PUT /api/applications/:id/status` - Update application status

## 🎨 UI Components

The platform features a modern, responsive design with:
- **Dashboard**: Personalized based on user role
- **Opportunity Browser**: Advanced filtering and search
- **Mentorship Matching**: Smart mentor-student pairing
- **Profile Management**: Comprehensive user profiles
- **Communication Hub**: Direct messaging and notifications

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Input validation and sanitization
- CORS protection
- Rate limiting
- SQL injection prevention

## 📱 Responsive Design

Fully responsive design optimized for:
- Desktop computers
- Tablets
- Mobile devices
- Various screen sizes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions, please contact the development team or create an issue in the repository.