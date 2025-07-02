# Ping! Chat

A simple, efficient web-based real-time chat system, focused on learning and practicing WebSocket technology. Built with **Vue 3 (frontend)** and **Flask (backend)**, Ping! Chat demonstrates the full-stack development workflow of modern web applications, including RESTful API design, WebSocket-based real-time messaging, and collaborative team development.

> **GitHub Repository:** https://github.com/ctq333/PingChat

------

## Project Objectives

The main goal of this experiment is to **design and implement a concise and efficient real-time chat system**. The project is not just about building a "usable" chat tool, but about combining and applying frontend and backend skills learned in class, understanding the full-stack web application workflow, and mastering modern real-time web technologies—especially WebSocket.

**Learning outcomes:**

- Deeply understand frontend-backend separation: Vue 3 + Flask API integration.
- Hands-on with RESTful API design, multi-table modeling, and SQL query optimization.
- Master WebSocket protocol for real-time messaging.
- Gain practical experience in team collaboration, code review, Git-based workflow, and project documentation.

------

### Database Design

- **users:** User info (username, password [hashed], nickname, avatar, admin/disabled, timestamps).
- **messages:** All chat messages; supports 1-to-1 and group (sender, receiver/group, type, content, status, timestamps, extra JSON).
- **groupchat:** Group info (name, avatar, announcement, owner).
- **group_members:** Many-to-many: group <-> members, with roles (admin, muted).
- **friends:** For future expansion (remarks, blacklist).
- **user_login_logs:** Security/audit (login time, IP, device, status).
- **message_receipts:** Message delivery/read status, esp. for group.

**Relationships:**
 Users ↔️ Messages (one-to-many)
 Groups ↔️ Members (many-to-many)
 Messages ↔️ Receipts (one-to-many)

### Tech Stack

- **Frontend:** Vue 3 (Composition API, Vue Router, Tailwind CSS, Material Symbols)
- **Backend:** Python Flask, Flask-SocketIO, SQLAlchemy, MySQL
- **WebSocket:** Real-time communication (native or socket.io)
- **Other:** IndexedDB (local image/message cache), Git (version control), Postman (API testing), VSCode (IDE)

### Implementation Overview

- **Frontend:** Modular Vue components (message cards, contact lists, chat input, etc.), clean UI/UX, real-time updates via WebSocket.
- **Backend:** Flask RESTful API, data handled in JSON, clear API structure, easy WebSocket integration.
- **Database:** Focused, extensible models, with JSON/ENUM fields for future-proofing.
- **Development:** Git for collaboration, incremental feature delivery.
- **Principle:** "Working first, then polish"—build core, then optimize.

------

## Key Features & System Architecture

### 1. User Registration & Login

- Username uniqueness ensured at registration.
- Passwords validated for length/security.
- Successful login returns user info (ID, roles, token), saved in local/session storage.
- Logout clears local/session storage and redirects to login.

### 2. Admin Features

- Modern admin dashboard (Vue 3 + Tailwind).
- User management: view all users, assign/revoke admin, enable/disable/mute users, delete, force logout.
- Online user management: real-time online list, force logout.
- Chat monitor: filter/search chat records by user/group/keyword/time.

### 3. Contacts & Groups

- After login, fetch system users, joined groups, and latest messages.
- Sorted by recent activity or username.

### 4. Private Chat

- WebSocket-based real-time messaging.
- Messages saved to DB, then pushed to clients.
- Image messages previewable in full screen.
- Clean, avatar-free UI for simplicity.

### 5. Group Chat

- WebSocket-based group messaging.
- Group creation (invite multiple users), add/remove members, dissolve group.
- Group avatars auto-generated from usernames.
- Group messages broadcasted to all members, stored in DB and IndexedDB.

### 6. Image Local Storage & History Sync

- Images stored in browser IndexedDB; upon message receipt, base64 data saved locally.
- When exporting or viewing history, images fetched from local DB.
- "Clear cache" button deletes local image/message cache.

### 7. Chat History Export

- Export text+image messages as HTML (images in base64).
- Supports full chat export and single message export.

### 8. Administrator Interface

- Visual, modular admin dashboard (Nuxt UI).
- Real-time user monitoring, group management, chat log access.

------

## UI & Operation Guide

### 1. Registration & Login

- Enter username and password to login.
- Registration checks for uniqueness and password strength.

### 2. Main Chat Interface

- After login, select any contact/group to open chat.
- Private chats: no avatar; group chats: auto-generated avatars.
- Send/receive text and images; images stored locally for offline access.

### 3. Group Management

- Create group: select multiple members.
- Add/remove members, dissolve group, manage group info.

### 4. Local Storage & History

- Images/messages synced to local IndexedDB.
- "Clear image cache" button in settings.

### 5. Message Export

- Export full chat or single messages (including images) as HTML files.

### 6. Admin Panel

- Access management functions, monitor users and messages, control group/user states.

------

## Key Source Code Highlights

> For detailed code, please refer to the repository. Below are key implementation points.

### 1. WebSocket

- Connection/disconnection, room join/leave, message event handling.
- Admin: force logout users via socket event.
- Group: socket broadcast for group events/messages.
- Image messages: handled as base64/Blob via WebSocket.

### 2. Conversation List

- Fetch and merge personal and group conversations, sorted by activity.

### 3. Private Chat

- Sending/receiving text and images, fullscreen image preview.

### 4. Group Chat

- Group creation, member management, dissolution, real-time messaging.

### 5. Local Storage & Export

- Save images to IndexedDB, sync with server, batch export as HTML.

### 6. Admin Functions

- Force logout, user status management, chat record queries.

------

## Experiment Summary

This project focused on **WebSocket implementation** for real-time chat, covering private/group chat, admin online management, and user force logout. The team emphasized modularity and efficient collaboration, with code structure designed for teamwork from the start.

**Main challenges:**

- WebSocket message sync: occasional out-of-order or missed messages, solved by adding message IDs and sorting/de-duplication on client.
- Data type inconsistencies (int vs. str for user_id), causing push and logout failures; strict typing solved this.
- Parameter naming inconsistencies (userId vs. user_id) caused hard-to-find bugs; standardized naming reduced issues.

**Innovations:**

- **IndexedDB**: local image cache and message persistence for better offline/media handling.
- **Modern admin UI**: modular, responsive, visually clean (Nuxt UI).
- **HTML export**: text+image chats exported as portable HTML with inline images for full offline access.

