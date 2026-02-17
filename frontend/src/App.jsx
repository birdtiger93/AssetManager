import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./Dashboard";
import Trade from "./Trade";
import { LayoutDashboard, TrendingUp } from "lucide-react";

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-100 flex flex-col">
          <div className="p-6 border-b border-gray-50">
            <h1 className="text-xl font-bold text-gray-800">KIS Manager</h1>
          </div>
          <nav className="flex-1 p-4 space-y-2">
            <NavLink to="/" icon={<LayoutDashboard size={20} />} label="Dashboard" />
            <NavLink to="/trade" icon={<TrendingUp size={20} />} label="Trade" />
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/trade" element={<Trade />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

const NavLink = ({ to, icon, label }) => (
  <Link
    to={to}
    className="flex items-center gap-3 px-4 py-3 text-gray-600 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
  >
    {icon}
    <span className="font-medium">{label}</span>
  </Link>
);

export default App;
