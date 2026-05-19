import {
  BarChart3,
  ClipboardCheck,
  FileText,
  History,
  Settings,
  Table2,
} from "lucide-react";
import SamplingScreen from "./features/sampling/SamplingScreen";

const navItems = [
  { label: "项目", Icon: Table2 },
  { label: "数据集", Icon: Table2 },
  { label: "抽样检验", Icon: ClipboardCheck },
  { label: "统计分析", Icon: BarChart3 },
  { label: "报告", Icon: FileText },
  { label: "审计日志", Icon: History },
  { label: "设置", Icon: Settings },
];

export default function App() {
  return (
    <main className="app-shell">
      <aside className="sidebar">
        <h1>医疗器械统计工作台</h1>
        <nav aria-label="主导航">
          {navItems.map(({ label, Icon }) => (
            <button type="button" key={label}>
              <Icon size={18} aria-hidden="true" />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>
      <section className="workspace">
        <SamplingScreen />
      </section>
    </main>
  );
}
