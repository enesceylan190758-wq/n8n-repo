-- 2. klinik: Clinic Mja Kartal (pilot sonrası platform testi)
-- whatsapp_phone bilerek yok — sonra eklenecek

INSERT INTO clinics (
  id,
  name,
  slug,
  logo_url,
  website_url,
  email,
  address,
  booking_url,
  google_maps_url,
  google_review_url,
  google_rating,
  google_review_count,
  whatsapp_phone
)
VALUES (
  'f8a2b14c-9d3e-4f61-a872-3c5e7d904b21',
  'Clinic Mja Kartal',
  'clinic-mja-kartal',
  'https://mja.com.tr/wp-content/uploads/2024/08/8200647961348-941-mjalogo1-1-1.png',
  'https://mja.com.tr',
  'info@clinicmja.com',
  'Cevizli, Köroğlu Cd. No:3C, 34100 Kartal/İstanbul',
  'https://mja.com.tr/iletisim/',
  'https://maps.app.goo.gl/UFrcdaU9R5kf7jsj9',
  'https://www.google.com/maps/place/Clinic+Mja+A%C4%9F%C4%B1z+ve+Di%C5%9F+Sa%C4%9Fl%C4%B1%C4%9F%C4%B1+Poliklini%C4%9Fi/@40.910506,29.172683,17z/data=!3m1!4b1!4m6!3m5!1s0x14cac5a93db1a9a5:0x2faab0c2b10ad229!8m2!3d40.910506!4d29.172683!16s%2Fg%2F11qr9fy8cy',
  4.7,
  100,
  NULL
)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  slug = EXCLUDED.slug,
  logo_url = EXCLUDED.logo_url,
  website_url = EXCLUDED.website_url,
  email = EXCLUDED.email,
  address = EXCLUDED.address,
  booking_url = EXCLUDED.booking_url,
  google_maps_url = EXCLUDED.google_maps_url,
  google_review_url = EXCLUDED.google_review_url,
  google_rating = EXCLUDED.google_rating,
  google_review_count = EXCLUDED.google_review_count;
