import type { Job } from './types';

const SAMPLE: Job[] = [
  { id: 'sample-1', title: 'Full Stack Developer', company: 'Acme Tech', location: 'Bengaluru', url: '#', salary: null,
    description: 'We need a full stack developer with React, JavaScript, Node.js and MongoDB. Experience with Docker, Git and REST APIs is required. TypeScript is a plus.' },
  { id: 'sample-2', title: 'Python Backend Developer', company: 'DataNest', location: 'Pune', url: '#', salary: null,
    description: 'Python backend role building APIs with Django or FastAPI, PostgreSQL, Redis and Docker. Knowledge of AWS and CI/CD is expected. Strong SQL required.' },
  { id: 'sample-3', title: 'Data Analyst', company: 'InsightWorks', location: 'Hyderabad', url: '#', salary: null,
    description: 'Data analyst with SQL, Python, Pandas, Excel and Power BI. Statistics and data visualization skills needed. Tableau is a plus.' },
  { id: 'sample-4', title: 'Frontend Engineer', company: 'PixelForge', location: 'Remote', url: '#', salary: null,
    description: 'Frontend engineer skilled in React, TypeScript, Next.js, HTML, CSS and Tailwind CSS. Testing with Jest. Git and Figma handoff experience.' },
  { id: 'sample-5', title: 'DevOps Engineer', company: 'CloudLoom', location: 'Noida', url: '#', salary: null,
    description: 'DevOps engineer with Linux, Docker, Kubernetes, Terraform, AWS and CI/CD pipelines. Python or Bash scripting required.' },
];

export type JobQuery = { what?: string; whatOr?: string; where?: string; page?: number };

export async function fetchJobs(q: JobQuery): Promise<{ jobs: Job[]; live: boolean }> {
  const id = process.env.ADZUNA_APP_ID;
  const key = process.env.ADZUNA_APP_KEY;
  if (!id || !key) return { jobs: SAMPLE, live: false };

  const params = new URLSearchParams({ app_id: id, app_key: key, results_per_page: '20', 'content-type': 'application/json' });
  if (q.what) params.set('what', q.what);
  if (q.whatOr) params.set('what_or', q.whatOr);
  if (q.where) params.set('where', q.where);

  try {
    const res = await fetch(`https://api.adzuna.com/v1/api/jobs/in/search/${q.page ?? 1}?${params}`, { next: { revalidate: 3600 } });
    if (!res.ok) throw new Error(String(res.status));
    const data = await res.json();
    const jobs: Job[] = (data.results ?? []).map((r: any) => ({
      id: String(r.id),
      title: r.title?.replace(/<[^>]+>/g, '') ?? 'Untitled',
      company: r.company?.display_name ?? 'Unknown company',
      location: r.location?.display_name ?? '',
      description: (r.description ?? '').replace(/<[^>]+>/g, ''),
      url: r.redirect_url ?? '#',
      salary: r.salary_min ? `₹${Math.round(r.salary_min).toLocaleString('en-IN')}+` : null,
      created: r.created,
    }));
    return { jobs, live: true };
  } catch {
    return { jobs: SAMPLE, live: false };
  }
}
