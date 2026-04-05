export const SITE_URL = "https://mosexmacchinalab.com" as const;

export const REPO_URL = "https://github.com/CuevazaArt/ethical-android-mvp" as const;

export const repoFile = (path: string) => `${REPO_URL}/blob/main/${path}`;

export const REPO_NEW_ISSUE = `${REPO_URL}/issues/new`;
export const REPO_ISSUE_COLLAB = `${REPO_URL}/issues/new?template=collaboration.yml`;
export const REPO_ISSUE_QUESTION = `${REPO_URL}/issues/new?template=question.yml`;
export const REPO_ISSUE_BUG = `${REPO_URL}/issues/new?template=bug_report.yml`;
