import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import Dashboard from "./Dashboard";
import Trade from "./Trade";
import Assets from "./Assets";
import ProfitLossPage from "./ProfitLossPage";
import { LayoutDashboard, TrendingUp, ChevronLeft, ChevronRight, Wallet, ChevronDown, PieChart, LineChart } from "lucide-react";

function AppContent() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const location = useLocation();

  return (
    <div className="flex h-screen bg-gray-50 font-sans text-gray-900">
      {/* Sidebar */}
      <aside
        className={`${isSidebarOpen ? "w-64" : "w-20"
          } bg-white border-r border-gray-100 flex flex-col transition-all duration-300 ease-in-out relative shadow-sm z-20`}
      >
        {/* Header / Logo */}
        <div className={`h-16 flex items-center ${isSidebarOpen ? "justify-between px-6" : "justify-center"} border-b border-gray-50`}>
          {isSidebarOpen ? (
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent tracking-tight">
              AssetManager
            </h1>
          ) : (
            <span className="text-xl font-bold text-blue-600">AM</span>
          )}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className={`p-1.5 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors ${!isSidebarOpen && "hidden"}`}
          >
            <ChevronLeft size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-2 mt-4">

          {/* Dashboard Group */}
          <NavGroup
            label="Dashboard"
            icon={<LayoutDashboard size={22} />}
            isOpen={isSidebarOpen}
            isActive={location.pathname === "/" || location.pathname === "/profit-loss"}
            basePath="/"
          >
            <NavLink
              to="/"
              icon={<PieChart size={18} />}
              label="Overview"
              isOpen={true} // Always open inside group
              isActive={location.pathname === "/"}
              isSubItem={true}
            />
            <NavLink
              to="/profit-loss"
              icon={<LineChart size={18} />}
              label="Profit & Loss"
              isOpen={true}
              isActive={location.pathname === "/profit-loss"}
              isSubItem={true}
            />
          </NavGroup>

          <NavLink
            to="/assets"
            icon={<Wallet size={22} />}
            label="Assets"
            isOpen={isSidebarOpen}
            isActive={location.pathname === "/assets"}
          />
          <NavLink
            to="/trade"
            icon={<TrendingUp size={22} />}
            label="Trade"
            isOpen={isSidebarOpen}
            isActive={location.pathname === "/trade"}
          />
        </nav>

        {/* Collapsed Toggle (if hidden in header) */}
        {!isSidebarOpen && (
          <div className="p-4 flex justify-center border-t border-gray-50">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition-colors"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-gray-50/50">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/assets" element={<Assets />} />
          <Route path="/trade" element={<Trade />} />
          <Route path="/profit-loss" element={<ProfitLossPage />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

const NavGroup = ({ label, icon, isOpen, isActive, children, basePath }) => {
  const [expanded, setExpanded] = useState(true);

  // Auto-expand if active
  useEffect(() => {
    if (isActive) setExpanded(true);
  }, [isActive]);

  if (!isOpen) {
    // Collapsed state: Behaves like a link to base path
    return (
      <Link
        to={basePath}
        className={`flex justify-center items-center p-3 rounded-xl transition-all duration-200 group relative
          ${isActive ? "bg-blue-50 text-blue-600" : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"}
        `}
      >
        <div className={`transition-colors duration-200 ${!isActive ? "text-gray-400 group-hover:text-gray-600" : ""}`}>
          {icon}
        </div>

        {/* Tooltip */}
        <div className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap pointer-events-none shadow-lg">
          {label}
        </div>
      </Link>
    );
  }

  return (
    <div className="space-y-1">
      <button
        onClick={() => setExpanded(!expanded)}
        className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group
          ${isActive ? "text-blue-700 font-semibold bg-blue-50/50" : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"}
        `}
      >
        <div className={`transition-colors duration-200 ${!isActive ? "text-gray-400 group-hover:text-gray-600" : "text-blue-600"}`}>
          {icon}
        </div>
        <span className="flex-1 text-left">{label}</span>
        <ChevronDown
          size={16}
          className={`text-gray-400 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
        />
      </button>

      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${expanded ? "max-h-40 opacity-100" : "max-h-0 opacity-0"
          }`}
      >
        <div className="space-y-1 pl-4 mb-2">
          <div className="border-l-2 border-gray-100 pl-2 space-y-1">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

const NavLink = ({ to, icon, label, isOpen, isActive, isSubItem = false }) => {
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group relative
            ${isActive
          ? "bg-blue-50 text-blue-600 shadow-sm"
          : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
        }
            ${!isOpen && "justify-center"}
            ${isSubItem ? "py-2 text-sm" : ""}
        `}
    >
      <div className={`transition-colors duration-200 ${!isOpen && !isActive ? "text-gray-400 group-hover:text-gray-600" : ""}`}>
        {icon}
      </div>

      <span
        className={`font-medium whitespace-nowrap transition-all duration-200 origin-left
            ${isOpen ? "opacity-100 w-auto" : "opacity-0 w-0 overflow-hidden"}
            `}
      >
        {label}
      </span>

      {/* Tooltip for collapsed state */}
      {!isOpen && (
        <div className="absolute left-full ml-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap pointer-events-none shadow-lg">
          {label}
        </div>
      )}
    </Link>
  );
};

export default App;
