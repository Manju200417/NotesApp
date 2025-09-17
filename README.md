**NotesApp**  

NotesApp is a web application designed to help students and educators upload, manage, preview, and download academic notes efficiently. It provides a structured way to store files along with detailed metadata, making it easy to search and retrieve notes. The application is fully mobile responsive, ensuring seamless use on smartphones, tablets, and desktops.

**Features**

 - Title: Name of the note.
 - Description: Brief overview of the content.
 - Category: Textbook, Notes, Previous Question Paper.
 - Year: 1st, 2nd, 3rd.
 - Branch: Computer Science, Electronics and Communication, Mechanical, Civil, Electrical.
 - Semester: 1 to 6.
 - Subject: Name of the subject.
 - File: Main file containing the notes.

**File Preview & Download**

 - Users can preview uploaded files directly in the application. Files
 - can also be downloaded for offline use.

**User Info Page**
 - After login, users can access a User Info page or button on the dashboard.
 - Displays the currently logged-in user’s details such as username and email.


**Database Design**
*The app uses a two-database system for performance and scalability:*

  

**SQLite**
 - **Users Table:** Stores user information (username, password, email).
 - **Files_Metadata Table**: Stores metadata of all uploaded files (Title, Description, Category, Year, Branch, Semester, Subject, File reference) for fast lookups and frontend display.

**MySQL**
 - Stores the actual file content with references to metadata (file ID, file data).

**Authentication & Authorization**
 - Users must be authenticated to upload, preview, or download files.
 - Admins have a dedicated Admin Page to view all registered users and delete uploaded files if needed.
 - Sessions track user activity across pages.
 - Middleware ensures users can only access authorized pages; public pages like login, register, admin login, and dashboard are excluded from this check.

  
**User-Friendly Interface**

 - Intuitive frontend to search, filter, preview, and download notes easily.
 - Fully mobile responsive for use on smartphones, tablets, and desktops.

**Secure File Management**

By separating metadata and file data into different databases, the app ensures faster lookups, efficient storage, and controlled access.

**Technology Stack**

 - Frontend: HTML, CSS
 - Backend: Flask (Python)
 - Databases: SQLite (user info and file metadata), MySQL (file storage)
