-- social_posts: 'ready' = Drive/local'e yüklendi, Instagram manuel planlanacak
ALTER TABLE social_posts DROP CONSTRAINT IF EXISTS social_posts_status_check;
ALTER TABLE social_posts ADD CONSTRAINT social_posts_status_check CHECK (status IN (
  'draft', 'pending_approval', 'approved', 'scheduled', 'ready', 'published', 'rejected', 'failed'
));
