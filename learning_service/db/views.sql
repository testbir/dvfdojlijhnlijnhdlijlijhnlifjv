DO $$
BEGIN
  -- v_enrollments
  IF to_regclass('catalog.courses_courseaccess') IS NOT NULL THEN
    EXECUTE $v$
      CREATE OR REPLACE VIEW learning.v_enrollments AS
      SELECT user_id, course_id, purchased_at AS acquired_at
      FROM catalog.courses_courseaccess
    $v$;
  ELSE
    EXECUTE $v$
      CREATE OR REPLACE VIEW learning.v_enrollments AS
      SELECT user_id, course_id, purchased_at AS acquired_at
      FROM courses_courseaccess
    $v$;
  END IF;

  -- v_modules
  IF to_regclass('catalog.courses_module') IS NOT NULL THEN
    EXECUTE $v$
      CREATE OR REPLACE VIEW learning.v_modules AS
      SELECT id, course_id, "order", title, COALESCE(sp_reward, 0) AS sp_reward
      FROM catalog.courses_module
    $v$;
  ELSE
    EXECUTE $v$
      CREATE OR REPLACE VIEW learning.v_modules AS
      SELECT id, course_id, "order", title, COALESCE(sp_reward, 0) AS sp_reward
      FROM courses_module
    $v$;
  END IF;
END $$;
