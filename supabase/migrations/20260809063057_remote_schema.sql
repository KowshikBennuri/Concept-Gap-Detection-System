-- Migration unit 1: schema_changes
-- Transaction mode: transactional
-- Boundary reason: default

DROP EXTENSION pg_net;

CREATE ROLE supabase_privileged_role;

GRANT supabase_privileged_role TO postgres;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT DELETE, INSERT, SELECT, UPDATE ON TABLES TO anon;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT, USAGE ON SEQUENCES TO anon;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON ROUTINES TO anon;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT DELETE, INSERT, SELECT, UPDATE ON TABLES TO authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT, USAGE ON SEQUENCES TO authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON ROUTINES TO authenticated;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT DELETE, INSERT, SELECT, UPDATE ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT, USAGE ON SEQUENCES TO service_role;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON ROUTINES TO service_role;

CREATE TABLE public.attempts (
  id               uuid                     DEFAULT gen_random_uuid() NOT NULL,
  student_id       uuid,
  concept_id       uuid,
  transcript       text,
  similarity_score double precision,
  eqs_score        double precision,
  missing_keywords text[],
  created_at       timestamp with time zone DEFAULT now(),
  minilm_score     double precision,
  mpnet_score      double precision,
  roberta_score    double precision,
  rouge_l          double precision,
  bert_score       double precision,
  tfidf_score      double precision,
  rouge1           double precision,
  rouge2           double precision
);

ALTER TABLE public.attempts
  ADD CONSTRAINT attempts_pkey PRIMARY KEY (id);

GRANT ALL ON public.attempts TO anon;

GRANT ALL ON public.attempts TO authenticated;

GRANT ALL ON public.attempts TO service_role;

CREATE POLICY "Allow All for Auth" ON public.attempts
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE TABLE public.enrollments (
  id         uuid DEFAULT gen_random_uuid() NOT NULL,
  student_id uuid,
  subject_id uuid
);

ALTER TABLE public.enrollments
  ADD CONSTRAINT enrollments_pkey PRIMARY KEY (id);

ALTER TABLE public.enrollments
  ADD CONSTRAINT enrollments_student_id_subject_id_key UNIQUE (student_id, subject_id);

GRANT ALL ON public.enrollments TO anon;

GRANT ALL ON public.enrollments TO authenticated;

GRANT ALL ON public.enrollments TO service_role;

CREATE POLICY "Allow All for Auth" ON public.enrollments
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE TABLE public.knowledge_base (
  id           uuid                     DEFAULT gen_random_uuid() NOT NULL,
  subject_id   uuid,
  concept_name text,
  ideal_answer text,
  keywords     text[],
  created_at   timestamp with time zone DEFAULT now()
);

ALTER TABLE public.knowledge_base
  ADD CONSTRAINT knowledge_base_pkey PRIMARY KEY (id);

ALTER TABLE public.attempts
  ADD CONSTRAINT attempts_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.knowledge_base(id) ON DELETE CASCADE;

GRANT ALL ON public.knowledge_base TO anon;

GRANT ALL ON public.knowledge_base TO authenticated;

GRANT ALL ON public.knowledge_base TO service_role;

CREATE POLICY "Full Access Knowledge Base" ON public.knowledge_base
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE TABLE public.profiles (
  id         uuid                     NOT NULL,
  full_name  text,
  role       text,
  created_at timestamp with time zone DEFAULT now()
);

ALTER TABLE public.profiles
  ADD CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;

ALTER TABLE public.profiles
  ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);

ALTER TABLE public.attempts
  ADD CONSTRAINT attempts_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.profiles(id) ON DELETE CASCADE;

ALTER TABLE public.enrollments
  ADD CONSTRAINT enrollments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.profiles(id) ON DELETE CASCADE;

GRANT ALL ON public.profiles TO anon;

GRANT ALL ON public.profiles TO authenticated;

GRANT ALL ON public.profiles TO service_role;

CREATE POLICY "Allow All for Auth" ON public.profiles
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow Profile Creation" ON public.profiles
  FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);

CREATE TABLE public.subjects (
  id         uuid                     DEFAULT gen_random_uuid() NOT NULL,
  name       text                     NOT NULL,
  faculty_id uuid,
  created_at timestamp with time zone DEFAULT now()
);

ALTER TABLE public.subjects
  ADD CONSTRAINT subjects_faculty_id_fkey FOREIGN KEY (faculty_id) REFERENCES public.profiles(id) ON DELETE CASCADE;

ALTER TABLE public.subjects
  ADD CONSTRAINT subjects_pkey PRIMARY KEY (id);

ALTER TABLE public.enrollments
  ADD CONSTRAINT enrollments_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;

ALTER TABLE public.knowledge_base
  ADD CONSTRAINT knowledge_base_subject_id_fkey FOREIGN KEY (subject_id) REFERENCES public.subjects(id) ON DELETE CASCADE;

GRANT ALL ON public.subjects TO anon;

GRANT ALL ON public.subjects TO authenticated;

GRANT ALL ON public.subjects TO service_role;

CREATE POLICY "Allow All for Auth" ON public.subjects
  TO authenticated
  USING (true)
  WITH CHECK (true);
