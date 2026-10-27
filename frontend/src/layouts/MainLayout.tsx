// Main application layout for DevOps Incident Commander
import React, { useState, createContext, useContext, ReactNode, useEffect } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import {
  Menu,
  AlertTriangle,
  BarChart3,
  Clock,
  Settings,
  User,
  Bell,
  ChevronLeft,
  ChevronRight,
  LogOut,
  HelpCircle,
  Home,
  Sparkles,
} from 'lucide-react';
import { cn } from '@utils/cn';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';

interface PageTitleContextType {
  title: string;
  description?: string;
  breadcrumbs?: Array<{ label: string; href?: string }>;
  setPageTitle: (title: string, description?: string, breadcrumbs?: Array<{ label: string; href?: string }>) => void;
}

const PageTitleContext = createContext<PageTitleContextType | undefined>(undefined);

export function usePageTitle() {
  const context = useContext(PageTitleContext);
  if (!context) {
    return {
      title: '',
      description: '',
      breadcrumbs: [],
      setPageTitle: () => {},
    };
  }
  return context;
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Incidents', href: '/incidents', icon: AlertTriangle },
  { name: 'Timeline', href: '/timeline', icon: Clock },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

type NavItemProps = {
  item: typeof navigation[0];
  isActive: boolean;
  sidebarCollapsed: boolean;
  onClick: () => void;
};

function NavItem({ item, isActive, sidebarCollapsed, onClick }: NavItemProps) {
  const Icon = item.icon;
  return (
    <Link
      to={item.href}
      className={cn(
        'sidebar-nav-link',
        isActive && 'sidebar-nav-link-active',
        sidebarCollapsed && 'sidebar-nav-link-collapsed'
      )}
      onClick={onClick}
      title={sidebarCollapsed ? item.name : undefined}
      aria-current={isActive ? 'page' : undefined}
    >
      {isActive && <span className="sidebar-nav-indicator" aria-hidden="true" />}
      <Icon className="h-[1.15rem] w-[1.15rem] flex-shrink-0" aria-hidden="true" />
      {!sidebarCollapsed && <span className="truncate">{item.name}</span>}
    </Link>
  );
}

function Sidebar({
  sidebarOpen,
  setSidebarOpen,
  sidebarCollapsed,
  setSidebarCollapsed,
  user,
  onSignOut,
}: {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  user: { name?: string; email?: string } | null;
  onSignOut: () => void;
}) {
  const location = useLocation();
  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  return (
    <>
      {sidebarOpen && (
        <button
          type="button"
          className="sidebar-overlay lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close navigation menu"
        />
      )}

      <aside
        className={cn(
          'app-sidebar',
          sidebarCollapsed && 'app-sidebar-collapsed',
          sidebarOpen ? 'app-sidebar-open' : 'app-sidebar-closed'
        )}
        aria-label="Main navigation"
      >
        <div className="sidebar-inner">
          <div className={cn('sidebar-brand', sidebarCollapsed && 'sidebar-brand-collapsed')}>
            {sidebarCollapsed ? (
              <div className="sidebar-logo-mark" aria-hidden="true">
                <AlertTriangle className="h-5 w-5 text-white" />
              </div>
            ) : (
              <div className="flex items-center gap-3 min-w-0">
                <div className="sidebar-logo-mark">
                  <AlertTriangle className="h-5 w-5 text-white" aria-hidden="true" />
                </div>
                <div className="min-w-0">
                  <span className="block text-sm font-semibold text-white tracking-tight truncate">
                    Incident Commander
                  </span>
                  <span className="block text-[10px] uppercase tracking-wider text-slate-500 font-medium">
                    AI Ops Platform
                  </span>
                </div>
              </div>
            )}
            <button
              type="button"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="sidebar-collapse-btn hidden lg:inline-flex"
              aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              aria-expanded={!sidebarCollapsed}
            >
              {sidebarCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </button>
          </div>

          {!sidebarCollapsed && (
            <div className="sidebar-ai-banner">
              <Sparkles className="h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
              <span>AI-assisted investigations</span>
            </div>
          )}

          <nav className="sidebar-nav" role="navigation" aria-label="Main">
            {navigation.map((item) => (
              <NavItem
                key={item.name}
                item={item}
                isActive={isActive(item.href)}
                sidebarCollapsed={sidebarCollapsed}
                onClick={() => setSidebarOpen(false)}
              />
            ))}
          </nav>

          <div className={cn('sidebar-footer', sidebarCollapsed && 'sidebar-footer-collapsed')}>
            <div className="sidebar-user">
              <div className="sidebar-user-avatar" aria-hidden="true">
                <User className="h-4 w-4 text-indigo-300" />
              </div>
              {!sidebarCollapsed && (
                <div className="min-w-0">
                  <p className="text-xs font-medium text-white truncate">{user?.name || 'User'}</p>
                  <p className="text-[10px] text-slate-500 truncate">{user?.email || 'Administrator'}</p>
                </div>
              )}
            </div>
            <button
              type="button"
              className={cn('sidebar-signout', sidebarCollapsed && 'sidebar-signout-collapsed')}
              onClick={onSignOut}
            >
              <LogOut className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
              {!sidebarCollapsed && <span>Sign out</span>}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

function Header({
  setSidebarOpen,
  user,
  pageTitle,
  breadcrumbs,
}: {
  setSidebarOpen: (open: boolean) => void;
  user: { name?: string; email?: string } | null;
  pageTitle: string;
  breadcrumbs?: Array<{ label: string; href?: string }>;
}) {
  const { toast } = useToast();
  const displayTitle =
    breadcrumbs && breadcrumbs.length > 0
      ? breadcrumbs[breadcrumbs.length - 1]?.label || pageTitle
      : pageTitle;

  return (
    <header className="app-topbar shrink-0">
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <button
          type="button"
          className="lg:hidden inline-flex items-center justify-center p-2 rounded-lg shrink-0 topbar-menu-btn"
          onClick={() => setSidebarOpen(true)}
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </button>

        <p className="sm:hidden text-sm font-semibold topbar-title truncate min-w-0">{displayTitle}</p>

        <nav className="hidden sm:flex items-center gap-2 text-sm min-w-0" aria-label="Breadcrumb">
          {breadcrumbs && breadcrumbs.length > 0 ? (
            breadcrumbs.map((crumb, index) => (
              <React.Fragment key={`${crumb.label}-${index}`}>
                {crumb.href ? (
                  <Link to={crumb.href} className="topbar-breadcrumb-link truncate">
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="topbar-breadcrumb-current truncate max-w-[12rem]">{crumb.label}</span>
                )}
                {index < breadcrumbs.length - 1 && (
                  <ChevronRight className="h-4 w-4 text-[var(--app-muted)] flex-shrink-0" aria-hidden="true" />
                )}
              </React.Fragment>
            ))
          ) : (
            <h1 className="text-sm font-semibold topbar-title truncate">{pageTitle}</h1>
          )}
        </nav>
      </div>

      <div className="flex items-center gap-1 sm:gap-2">
        <button
          type="button"
          className="topbar-icon-btn relative"
          aria-label="Notifications"
          onClick={() =>
            toast({
              title: 'Notifications',
              description: 'Notification delivery is not configured in this demo environment.',
            })
          }
        >
          <Bell className="h-5 w-5" aria-hidden="true" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-rose-500" aria-hidden="true" />
        </button>

        <Link to="/settings" className="topbar-icon-btn hidden sm:inline-flex" aria-label="Help and settings">
          <HelpCircle className="h-5 w-5" aria-hidden="true" />
        </Link>

        <button
          type="button"
          className="topbar-user-btn"
          aria-label="User menu"
          onClick={() =>
            toast({
              title: 'Account',
              description: 'User profiles are not configured in this demo environment.',
            })
          }
        >
          <div className="h-8 w-8 rounded-full topbar-avatar flex items-center justify-center">
            <User className="h-4 w-4" aria-hidden="true" />
          </div>
          <span className="hidden sm:block text-sm font-medium topbar-user-name max-w-[8rem] truncate">
            {user?.name || 'User'}
          </span>
        </button>
      </div>
    </header>
  );
}

function PageTitleProvider({ children }: { children: ReactNode }) {
  const [title, setTitle] = useState('Dashboard');
  const [description, setDescription] = useState('');
  const [breadcrumbs, setBreadcrumbs] = useState<Array<{ label: string; href?: string }>>([]);

  const setPageTitle = React.useCallback(
    (newTitle: string, newDescription?: string, newBreadcrumbs?: Array<{ label: string; href?: string }>) => {
      setTitle(newTitle);
      setDescription(newDescription || '');
      setBreadcrumbs(newBreadcrumbs || []);
    },
    []
  );

  return (
    <PageTitleContext.Provider value={{ title, description, breadcrumbs, setPageTitle }}>
      {children}
    </PageTitleContext.Provider>
  );
}

export default function MainLayout() {
  return (
    <PageTitleProvider>
      <MainLayoutContent />
    </PageTitleProvider>
  );
}

function MainLayoutContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user } = useAuth();
  const { toast } = useToast();
  const { title, breadcrumbs } = usePageTitle();

  useEffect(() => {
    document.body.classList.add('app-layout-active');
    return () => document.body.classList.remove('app-layout-active');
  }, []);

  return (
    <div className={cn('app-shell', sidebarCollapsed && 'app-shell-collapsed')}>
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        sidebarCollapsed={sidebarCollapsed}
        setSidebarCollapsed={setSidebarCollapsed}
        user={user}
        onSignOut={() =>
          toast({
            title: 'Signed out',
            description: 'Authentication is not enabled in this demo environment.',
          })
        }
      />

      <div className="app-main">
        <Header setSidebarOpen={setSidebarOpen} user={user} pageTitle={title} breadcrumbs={breadcrumbs} />
        <main className="app-main-scroll" role="main">
          <div className="app-content animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
