export const password = "Password123!";
export const body = "I am building a Node.js service and need a safe retry pattern for idempotent HTTP requests. I have already tried a simple timeout wrapper, but I need guidance on exponential backoff, duplicate suppression, timeout handling, and observability across intermittent failures in production. What patterns should I use and how should I structure retries so the client remains correct, debuggable, and safe for repeated delivery attempts?";
export const answerBody = "Use exponential backoff together with an idempotency key so duplicate requests can be safely retried without creating duplicate side effects in downstream services.";
export const commentBody = "Can you share what you tried so far?";
export const retryTitle = "How can I safely retry an idempotent HTTP request in Node.js?";
export const accounts = {
  "stack_user": "stack_user@example.com",
  "question_creator": "question_creator@example.com",
  "question_editor": "question_editor@example.com",
  "question_deleter": "question_deleter@example.com",
  "question_upvoter": "question_upvoter@example.com",
  "answer_submitter": "answer_submitter@example.com",
  "helpful_user": "helpful_user@example.com",
  "answer_voter": "answer_voter@example.com",
  "answer_accept_owner": "answer_accept_owner@example.com",
  "question_comment_user": "question_comment_user@example.com",
  "comment_delete_user": "comment_delete_user@example.com"
} as const;
