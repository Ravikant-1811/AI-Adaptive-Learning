# Functional Flow

## Learner Flow
1. Register/Login
2. If no learning style: direct selection or MCQ test
3. Save style scores and dominant style
4. Open chat and ask question
5. Backend returns adaptive response:
   - Visual: structured explanation + visual assets
   - Auditory: explanation + audio file generation
   - Kinesthetic: guided steps + synced practice tasks
6. User opens practice lab, runs/submits Java code
7. User downloads task sheet / solution / pdf / audio
8. System stores chat, activity, and downloads

## Practice Sync Flow
1. User asks in chat
2. Chat response includes `practice` task bundle
3. Bundle stored in local state and backend logs
4. Practice page loads exact topic tasks from chat
5. Submission stored in `PracticeActivity`

## Admin Flow
1. Admin login
2. View users, chats, downloads, activity metrics
3. Monitor platform usage and learner progress
