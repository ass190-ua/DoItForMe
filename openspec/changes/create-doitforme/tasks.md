## 1. Project Setup
- [x] 1.1 Initialize Node.js + Express + TypeScript project
- [x] 1.2 Install Prisma and PostgreSQL dependencies
- [x] 1.3 Configure database connection

## 2. Database Schema
- [x] 2.1 Define User model in `schema.prisma`
- [x] 2.2 Define Task model in `schema.prisma`
- [x] 2.3 Define Offer model in `schema.prisma`
- [x] 2.4 Run Prisma migration to apply schema to database

## 3. Authentication
- [x] 3.1 Implement JWT authentication middleware
- [x] 3.2 Create User registration endpoint
- [x] 3.3 Create User login endpoint

## 4. User and Task Routes
- [x] 4.1 Create endpoint to list tasks
- [x] 4.2 Create endpoint for authenticated users to POST new tasks

## 5. Offers and Business Logic
- [x] 5.1 Create endpoint for runners to submit offers on tasks
- [x] 5.2 Create endpoint for creators to accept offers
- [x] 5.3 Implement database transaction to update Task and Offer states upon acceptance
- [x] 5.4 Ensure task self-offer and self-acceptance validations are implemented
