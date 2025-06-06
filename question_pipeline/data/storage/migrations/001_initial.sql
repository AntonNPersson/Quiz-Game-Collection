CREATE TABLE questions(
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE INDEX idx_questions_category ON questions(category);