# Educational Foundation Website - Image Assets

This directory contains all placeholder images for the Educational Foundation website.

## Directory Structure

### Hero Images (`/hero/`)
- `african-student.jpg` - Hero image for homepage (800x600)

### Program Images (`/programs/`)
- `mentorship.jpg` - Mentorship Program image (800x500)
- `academic-support.jpg` - Academic Support Program image (800x500)
- `career-guidance.jpg` - Career Guidance Program image (800x500)

### Staff Photos (`/staff/`)

**Leadership Team (400x400):**
- `nomsa-khumalo.jpg` - Dr. Nomsa Khumalo, Executive Director
- `sipho-ndlovu.jpg` - Sipho Ndlovu, Program Director
- `thandiwe-mabaso.jpg` - Thandiwe Mabaso, Operations Manager

**Program Staff (300x300):**
- `lerato-molefe.jpg` - Lerato Molefe, Mentorship Coordinator
- `bongani-dlamini.jpg` - Bongani Dlamini, Academic Support Specialist
- `zanele-sithole.jpg` - Zanele Sithole, Career Guidance Counselor
- `thabo-moyo.jpg` - Thabo Moyo, Volunteer Coordinator
- `precious-nkosi.jpg` - Precious Nkosi, Student Success Advisor
- `mandla-zulu.jpg` - Mandla Zulu, Scholarship Administrator

### Announcement Images (`/announcements/`)
All announcement images are 800x450:
- `mentorship-launch.jpg` - New Mentorship Program Launch
- `scholarship-gala.jpg` - Annual Scholarship Gala
- `thabo-graduation.jpg` - Student Success Story
- `volunteer-orientation.jpg` - Volunteer Orientation Day
- `coding-bootcamp.jpg` - Tech Partnership Coding Bootcamp
- `10-year-anniversary.jpg` - Foundation 10th Anniversary
- `career-fair.jpg` - Annual Career Fair
- `academic-success.jpg` - Academic Support Program Success

### About Page Images (`/about/`)
- `classroom.jpg` - Classroom image for About page story section (800x600)

### Contact Page Images
- `students-at-school.jpg` - Students at school image (1280x600)

## Image Format

All images are currently SVG placeholders with:
- Appropriate dimensions for their use case
- Color-coded backgrounds for easy identification
- Text labels indicating the image purpose
- Consistent sizing within each category

## Replacing Placeholders

To replace these placeholder images with actual photographs:
1. Ensure new images match the specified dimensions (or maintain aspect ratio)
2. Optimize images for web (compress, use WebP format with JPEG fallback)
3. Replace the SVG files with actual image files
4. Keep the same filenames to avoid breaking references

## Icon System

The website uses **Lucide Icons** (https://lucide.dev/) via CDN:
- CDN integrated in `templates/base.html`
- Icons initialized with `lucide.createIcons()`
- No emoji icons are used anywhere in the site
- Icons are implemented using `<i data-lucide="icon-name"></i>` syntax

### Icon Usage Throughout Site:
- Navigation: menu, x (close)
- Stats: users, trending-up, award, calendar
- Values: heart, target, zap, lightbulb, briefcase
- Programs: users, book-open, briefcase, check, check-circle
- Contact: map-pin, mail, phone, clock
- Social: facebook, twitter, instagram, linkedin
- Actions: arrow-right, info, user-check

All icons are properly integrated and no emoji characters are used.
