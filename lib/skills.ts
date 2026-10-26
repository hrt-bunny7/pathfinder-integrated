// Skill dictionary: canonical name -> aliases. SHARE THIS LIST with Member 3 so names match everywhere.
// Add more entries as you go; the matching engine picks them up automatically.
export const SKILLS: Record<string, string[]> = {
  Python: ['python', 'python3'], Java: ['java'], JavaScript: ['javascript', 'js', 'es6'], TypeScript: ['typescript'],
  'C++': ['c++'], C: ['c programming'], 'C#': ['c#'], Go: ['golang'], Rust: ['rust'], PHP: ['php'], Kotlin: ['kotlin'], Swift: ['swift'],
  R: ['r programming', 'rstudio'], HTML: ['html', 'html5'], CSS: ['css', 'css3'], Sass: ['sass', 'scss'],
  React: ['react', 'reactjs', 'react.js'], 'Next.js': ['next.js', 'nextjs'], Angular: ['angular', 'angularjs'], Vue: ['vue', 'vuejs', 'vue.js'],
  'Node.js': ['node.js', 'nodejs', 'node js'], Express: ['express', 'express.js', 'expressjs'], Django: ['django'], Flask: ['flask'], FastAPI: ['fastapi'],
  'Spring Boot': ['spring boot', 'springboot', 'spring'], '.NET': ['.net', 'dotnet', 'asp.net'], 'Tailwind CSS': ['tailwind', 'tailwindcss'], Bootstrap: ['bootstrap'],
  'REST APIs': ['rest api', 'rest apis', 'restful', 'rest'], GraphQL: ['graphql'], Microservices: ['microservices', 'microservice'],
  SQL: ['sql'], MySQL: ['mysql'], PostgreSQL: ['postgresql', 'postgres'], MongoDB: ['mongodb', 'mongo'], Redis: ['redis'], Firebase: ['firebase'], Supabase: ['supabase'],
  Git: ['git', 'github', 'gitlab', 'version control'], Docker: ['docker', 'containerization'], Kubernetes: ['kubernetes', 'k8s'], Linux: ['linux', 'unix', 'bash', 'shell scripting'],
  AWS: ['aws', 'amazon web services', 'ec2', 's3'], Azure: ['azure'], GCP: ['gcp', 'google cloud'], 'CI/CD': ['ci/cd', 'cicd', 'jenkins', 'github actions'], Terraform: ['terraform'],
  'Machine Learning': ['machine learning', 'ml'], 'Deep Learning': ['deep learning', 'neural networks'], NLP: ['nlp', 'natural language processing'],
  TensorFlow: ['tensorflow'], PyTorch: ['pytorch'], 'Scikit-learn': ['scikit-learn', 'sklearn'], Pandas: ['pandas'], NumPy: ['numpy'],
  'Data Analysis': ['data analysis', 'data analytics', 'analytics'], 'Data Visualization': ['data visualization', 'data visualisation'],
  'Power BI': ['power bi', 'powerbi'], Tableau: ['tableau'], Excel: ['excel', 'advanced excel'], Spark: ['spark', 'pyspark'], Hadoop: ['hadoop'], Statistics: ['statistics', 'statistical'],
  'Data Structures': ['data structures', 'dsa', 'algorithms'], 'System Design': ['system design'], OOP: ['oop', 'object oriented', 'object-oriented'],
  Testing: ['unit testing', 'jest', 'pytest', 'selenium', 'test automation'], Agile: ['agile', 'scrum', 'jira'],
  'React Native': ['react native'], Flutter: ['flutter'], Android: ['android'], iOS: ['ios'],
  Figma: ['figma'], 'UI/UX': ['ui/ux', 'ux design', 'ui design'], Communication: ['communication skills', 'communication'], 'Problem Solving': ['problem solving', 'problem-solving'],
  Cybersecurity: ['cybersecurity', 'cyber security', 'information security'], Networking: ['networking', 'tcp/ip'], 'Digital Marketing': ['digital marketing', 'seo'],
};

// Skills that are "close enough" to earn partial credit (50%) when the user has the related one
export const RELATED: [string, string][] = [
  ['Django', 'Flask'], ['Django', 'FastAPI'], ['Flask', 'FastAPI'], ['React', 'Vue'], ['React', 'Angular'], ['Vue', 'Angular'],
  ['MySQL', 'PostgreSQL'], ['SQL', 'MySQL'], ['SQL', 'PostgreSQL'], ['AWS', 'Azure'], ['AWS', 'GCP'], ['Azure', 'GCP'],
  ['TensorFlow', 'PyTorch'], ['Power BI', 'Tableau'], ['Java', 'Kotlin'], ['Java', 'C#'], ['Express', 'Node.js'], ['Next.js', 'React'],
  ['Docker', 'Kubernetes'], ['Machine Learning', 'Deep Learning'], ['Pandas', 'NumPy'], ['Flutter', 'React Native'],
];

// What to learn first. Used to order roadmaps (prerequisites come before the skills that need them)
export const PREREQS: Record<string, string[]> = {
  React: ['JavaScript', 'HTML', 'CSS'], 'Next.js': ['React'], Angular: ['TypeScript'], Vue: ['JavaScript'], TypeScript: ['JavaScript'],
  'Node.js': ['JavaScript'], Express: ['Node.js'], Django: ['Python'], Flask: ['Python'], FastAPI: ['Python'], 'Spring Boot': ['Java'],
  Pandas: ['Python'], NumPy: ['Python'], 'Scikit-learn': ['Python', 'Statistics'], 'Machine Learning': ['Python', 'Statistics'],
  'Deep Learning': ['Machine Learning'], TensorFlow: ['Deep Learning'], PyTorch: ['Deep Learning'], NLP: ['Machine Learning'],
  Kubernetes: ['Docker', 'Linux'], Docker: ['Linux'], Terraform: ['AWS'], 'CI/CD': ['Git'], 'React Native': ['React'],
  Microservices: ['REST APIs'], GraphQL: ['REST APIs'], 'System Design': ['Data Structures'], Spark: ['Python', 'SQL'],
};

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

// Pre-compile one regex per alias; boundaries handle names like c++, c#, node.js
const MATCHERS = Object.entries(SKILLS).flatMap(([name, aliases]) =>
  [name.toLowerCase(), ...aliases].map((a) => ({
    name,
    re: new RegExp(`(?<![a-z0-9+#.])${escapeRe(a)}(?![a-z0-9+#])`, 'g'),
  }))
);

/** Turn any spelling ("ReactJS", "react.js") into the canonical name, or null if unknown. */
export function canonicalSkill(raw: string): string | null {
  const t = raw.trim().toLowerCase();
  for (const [name, aliases] of Object.entries(SKILLS)) {
    if (name.toLowerCase() === t || aliases.includes(t)) return name;
  }
  return null;
}

/** Find skills in free text and weight them (more mentions + earlier mention = more important). */
export function extractSkills(text: string): { name: string; weight: number }[] {
  const lower = text.toLowerCase();
  const found = new Map<string, { count: number; first: number }>();
  for (const { name, re } of MATCHERS) {
    re.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(lower))) {
      const cur = found.get(name) ?? { count: 0, first: m.index };
      cur.count += 1;
      cur.first = Math.min(cur.first, m.index);
      found.set(name, cur);
    }
  }
  const len = Math.max(lower.length, 1);
  return [...found.entries()]
    .map(([name, { count, first }]) => ({
      name,
      weight: +(1 + Math.min(count - 1, 3) * 0.5 + (first / len < 0.3 ? 0.5 : 0)).toFixed(2),
    }))
    .sort((a, b) => b.weight - a.weight);
}
