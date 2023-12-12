# Multi-Tenant-Task-Management-System

This project is a task management API for teams using a multi-tenant architecture with shared schemas

## Users should be able to: 
- Create an account
- modify account data (if owner)
- Create a team
- See all teams that is part of
- Add members (if captain of the team)
- See team data (if user is in team)
- Leave a team or remove a member (if captain or first mate)
- Delete team (if captain)
- Be in many teams with different roles for each team

## Users shouldn't be able to:
- Use API if not JWT authenticated
- See another user data
- Modify another user data
- See other user teams
- See team data that is not part of
- Modify team data if doesn't have permission
