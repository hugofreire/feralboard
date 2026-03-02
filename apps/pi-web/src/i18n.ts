export type Language = "en" | "pt";

export const LANGUAGE_STORAGE_KEY = "feralboard-language";

const dictionaries: Record<Language, Record<string, string>> = {
  en: {
    portalTitle: "FeralBuilder",
    screen: "Screen",
    screenshot: "Screenshot",
    restart: "Restart",
    restartGui: "Restart GUI",
    kioskApps: "FeralBoard Apps",
    newApp: "New App",
    deviceScreen: "Device Screen",
    files: "Files",
    sessions: "Sessions",
    config: "Config",
    env: "Env",
    agent: "Agent",
    open: "Open",
    readyToCode: "Ready to code",
    describeTask: "Describe what you want the agent to do with {appName}",
    latestScreenshot: "Latest screenshot",
    describeInput: "Describe what you want the agent to do...",
    stop: "Stop",
    noFiles: "No files",
    noSessions: "No sessions yet",
    noApps: "No kiosk apps found. Create your first one!",
    save: "Save",
    addVariable: "Add Variable",
    noEnvVars: "No environment variables. Click \"Add Variable\" to create one.",
    name: "Name",
    description: "Description",
    type: "Type",
    greetingText: "Greeting Text",
    customPage: "Custom Page",
    customPageDesc: "GTK page with full control. Agent can edit the code.",
    greetingType: "Greeting",
    greetingTypeDesc: "Simple text shown on lock screen. No code needed.",
    willCreate: "Will create:",
    createApp: "Create App",
    light: "Light",
    dark: "Dark",
    switchToLight: "Switch to light mode",
    switchToDark: "Switch to dark mode",
    language: "Language",
    appJson: "app.json",
  },
  pt: {
    portalTitle: "FeralBuilder",
    screen: "Ecrã",
    screenshot: "Captura",
    restart: "Reiniciar",
    restartGui: "Reiniciar GUI",
    kioskApps: "FeralBoard Apps",
    newApp: "Nova App",
    deviceScreen: "Ecrã do Dispositivo",
    files: "Ficheiros",
    sessions: "Sessões",
    config: "Config",
    env: "Env",
    agent: "Agente",
    open: "Open",
    readyToCode: "Pronto para programar",
    describeTask: "Descreva o que pretende que o agente faça com {appName}",
    latestScreenshot: "Última captura",
    describeInput: "Descreva o que pretende que o agente faça...",
    stop: "Parar",
    noFiles: "Sem ficheiros",
    noSessions: "Ainda sem sessões",
    noApps: "Nenhum app encontrado. Crie o primeiro.",
    save: "Guardar",
    addVariable: "Adicionar Variável",
    noEnvVars: "Não existem variáveis de ambiente. Clique em \"Adicionar Variável\" para criar uma.",
    name: "Nome",
    description: "Descrição",
    type: "Tipo",
    greetingText: "Texto de Saudação",
    customPage: "Página Custom",
    customPageDesc: "Página GTK com controlo total. O agente pode editar o código.",
    greetingType: "Saudação",
    greetingTypeDesc: "Texto simples mostrado no ecrã de bloqueio. Sem código.",
    willCreate: "Vai ser criado:",
    createApp: "Criar App",
    light: "Claro",
    dark: "Escuro",
    switchToLight: "Mudar para modo claro",
    switchToDark: "Mudar para modo escuro",
    language: "Idioma",
    appJson: "app.json",
  },
};

export function getPreferredLanguage(): Language {
  const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
  if (stored === "en" || stored === "pt") return stored;
  return navigator.language.toLowerCase().startsWith("pt") ? "pt" : "en";
}

export function translate(language: Language, key: string, vars?: Record<string, string | number>) {
  let value = dictionaries[language][key] ?? dictionaries.en[key] ?? key;
  if (vars) {
    for (const [name, replacement] of Object.entries(vars)) {
      value = value.replaceAll(`{${name}}`, String(replacement));
    }
  }
  return value;
}
