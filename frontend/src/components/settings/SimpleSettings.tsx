// Settings component for DevOps Incident Commander
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Label } from '../ui/Label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Select';
import { Switch } from '../ui/Switch';
import { useToast } from '../../hooks/useToast';
import { usePageTitle } from '../../layouts/MainLayout';
import { cn } from '@utils/cn';
import { PageHeader } from '../ui/PageHeader';
import { useTheme } from '../../contexts/ThemeContext';
import { ACCENT_COLOR_OPTIONS } from '../../lib/theme';
import {
  Settings as SettingsIcon,
  Bell,
  Shield,
  Database,
  User,
  Palette,
  Save,
  Lock,
  AlertCircle,
  HelpCircle,
} from 'lucide-react';

export default function Settings() {
  const { toast } = useToast();
  const { setPageTitle } = usePageTitle();
  const { darkMode, primaryColor, setDarkMode, setPrimaryColor } = useTheme();
  const [loading, setLoading] = useState(false);
  const [activeSection, setActiveSection] = useState<'general' | 'notifications' | 'security' | 'api' | 'appearance' | 'account'>('general');

  // General settings
  const [generalSettings, setGeneralSettings] = useState({
    appName: 'DevOps Incident Commander',
    defaultIncidentStatus: 'open',
    defaultSeverity: 'medium',
    itemsPerPage: 10,
    timezone: 'UTC',
  });

  // Notification settings
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    slackNotifications: false,
    webhookNotifications: true,
    criticalAlertsOnly: false,
  });

  // Security settings
  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: true,
    sessionTimeout: 30,
    passwordExpiry: 90,
    requireStrongPassword: true,
  });

  // API configuration
  const [apiSettings, setApiSettings] = useState({
    apiUrl: import.meta.env.VITE_API_BASE_URL?.trim() || (import.meta.env.DEV ? '' : ''),
    apiTimeout: 30,
    retryAttempts: 3,
    rateLimit: 100,
  });

  // User settings
  const [userSettings, setUserSettings] = useState({
    email: '',
    displayName: '',
  });

  // Load saved settings on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('app-settings');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.general) setGeneralSettings(parsed.general);
        if (parsed.notifications) setNotificationSettings(parsed.notifications);
        if (parsed.security) setSecuritySettings(parsed.security);
        if (parsed.api) setApiSettings(parsed.api);
        if (parsed.user) setUserSettings(parsed.user);
      }
    } catch (e) {
      console.warn('Failed to load saved settings:', e);
    }
  }, []);

  // Set page title when component mounts
  useEffect(() => {
    setPageTitle('Settings', 'Configure your DevOps Incident Commander instance', [
      { label: 'Settings', href: '/settings' },
    ]);
  }, [setPageTitle]);

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      // Simulate API call - in production this would persist to backend
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Store settings locally for persistence across sessions
      const allSettings = {
        general: generalSettings,
        notifications: notificationSettings,
        security: securitySettings,
        api: apiSettings,
        appearance: { darkMode, primaryColor },
        user: userSettings,
      };
      localStorage.setItem('app-settings', JSON.stringify(allSettings));

      toast({
        title: "Settings saved",
        description: "Your settings have been successfully saved.",
      });
    } catch (error) {
      toast({
        title: "Error saving settings",
        description: "There was an error saving your settings. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const settingsSections = [
    { id: 'general', label: 'General', icon: SettingsIcon, description: 'Core application preferences' },
    { id: 'notifications', label: 'Notifications', icon: Bell, description: 'Configure how you receive alerts' },
    { id: 'security', label: 'Security', icon: Shield, description: 'Authentication and access control settings' },
    { id: 'api', label: 'API Configuration', icon: Database, description: 'Backend API connection settings' },
    { id: 'appearance', label: 'Appearance', icon: Palette, description: 'Customize the look and feel' },
    { id: 'account', label: 'User Account', icon: User, description: 'Your profile and credentials' },
  ] as const;

  const SectionCard = ({
    title,
    icon,
    description,
    children,
    className = ""
  }: {
    title: string;
    icon: React.ReactNode;
    description?: string;
    children: React.ReactNode;
    className?: string;
  }) => (
    <Card className={cn('section-card', className)}>
      <CardHeader className="section-card-header">
        <div className="section-card-title-row">
          <div className="section-card-icon">
            {icon}
          </div>
          <div>
            <CardTitle className="section-card-title">{title}</CardTitle>
            {description && <CardDescription className="section-card-description">{description}</CardDescription>}
          </div>
        </div>
      </CardHeader>
      <CardContent className="section-card-content">{children}</CardContent>
    </Card>
  );

  const Field = ({
    label,
    description,
    children,
    htmlFor,
    required = false
  }: {
    label: string;
    description?: string;
    children: React.ReactNode;
    htmlFor?: string;
    required?: boolean;
  }) => (
    <div className="field">
      <Label htmlFor={htmlFor} className="field-label">
        {label}
        {required && <span className="field-required" aria-hidden="true">*</span>}
      </Label>
      {description && <p className="field-description">{description}</p>}
      {children}
    </div>
  );

  const ToggleRow = ({
    label,
    description,
    checked,
    onChange,
    id
  }: {
    label: string;
    description?: string;
    checked: boolean;
    onChange: (checked: boolean) => void;
    id: string;
  }) => (
    <div className="toggle-row">
      <div className="toggle-label">
        <Label htmlFor={id} className="toggle-label-text">
          {label}
        </Label>
        {description && <p className="toggle-description">{description}</p>}
      </div>
      <Switch
        id={id}
        checked={checked}
        onCheckedChange={onChange}
        aria-label={label}
      />
    </div>
  );

  const InputWithLabel = ({
    label,
    description,
    type = 'text',
    value,
    onChange,
    id,
    placeholder,
    min,
    max,
    ...props
  }: {
    label: string;
    description?: string;
    type?: string;
    value: string | number;
    onChange: (value: string | number) => void;
    id: string;
    placeholder?: string;
    min?: number;
    max?: number;
  }) => (
    <Field label={label} description={description} htmlFor={id}>
      <Input
        id={id}
        type={type}
        value={value}
        onChange={(e) => onChange(type === 'number' ? (parseInt(e.target.value) || 0) : e.target.value)}
        placeholder={placeholder}
        min={min}
        max={max}
        className="w-full"
        {...props}
      />
    </Field>
  );

  const SelectWithLabel = ({
    label,
    description,
    value,
    onChange,
    id,
    options,
    placeholder,
    ...props
  }: {
    label: string;
    description?: string;
    value: string;
    onChange: (value: string) => void;
    id: string;
    options: { value: string; label: string }[];
    placeholder?: string;
  }) => (
    <Field label={label} description={description} htmlFor={id}>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger id={id} className="w-full">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {options.map(opt => (
            <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </Field>
  );

  const statusOptions = [
    { value: 'open', label: 'Open' },
    { value: 'investigating', label: 'Investigating' },
    { value: 'resolved', label: 'Resolved' },
    { value: 'closed', label: 'Closed' },
  ];

  const severityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' },
  ];

  const timezoneOptions = [
    { value: 'UTC', label: 'UTC' },
    { value: 'America/New_York', label: 'New York (EST/EDT)' },
    { value: 'America/Los_Angeles', label: 'Los Angeles (PST/PDT)' },
    { value: 'Europe/London', label: 'London (GMT/BST)' },
    { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
  ];

  const renderSection = (sectionId: string) => {
    switch (sectionId) {
      case 'general':
        return (
          <SectionCard
            title="General"
            icon={<SettingsIcon className="h-5 w-5" />}
            description="Core application preferences"
          >
            <div className="space-y-5">
              <InputWithLabel
                label="Application Name"
                description="Display name shown in the header"
                value={generalSettings.appName}
                onChange={(v) => setGeneralSettings(prev => ({ ...prev, appName: v as string }))}
                id="appName"
                placeholder="DevOps Incident Commander"
              />

              <SelectWithLabel
                label="Default Incident Status"
                description="Status assigned to new incidents"
                value={generalSettings.defaultIncidentStatus}
                onChange={(v) => setGeneralSettings(prev => ({ ...prev, defaultIncidentStatus: v }))}
                id="defaultIncidentStatus"
                options={statusOptions}
                placeholder="Select default status"
              />

              <SelectWithLabel
                label="Default Severity"
                description="Severity assigned to new incidents"
                value={generalSettings.defaultSeverity}
                onChange={(v) => setGeneralSettings(prev => ({ ...prev, defaultSeverity: v }))}
                id="defaultSeverity"
                options={severityOptions}
                placeholder="Select default severity"
              />

              <InputWithLabel
                label="Items Per Page"
                description="Number of items shown per page (5-100)"
                type="number"
                value={generalSettings.itemsPerPage}
                onChange={(v) => setGeneralSettings(prev => ({ ...prev, itemsPerPage: v as number }))}
                id="itemsPerPage"
                min={5}
                max={100}
              />

              <SelectWithLabel
                label="Timezone"
                description="Timezone for timestamps and scheduling"
                value={generalSettings.timezone}
                onChange={(v) => setGeneralSettings(prev => ({ ...prev, timezone: v }))}
                id="timezone"
                options={timezoneOptions}
                placeholder="Select timezone"
              />
            </div>
          </SectionCard>
        );

      case 'notifications':
        return (
          <SectionCard
            title="Notifications"
            icon={<Bell className="h-5 w-5" />}
            description="Configure how you receive alerts"
          >
            <div className="space-y-1">
              <ToggleRow
                label="Email Notifications"
                description="Receive incident alerts via email"
                checked={notificationSettings.emailNotifications}
                onChange={(checked) => setNotificationSettings(prev => ({ ...prev, emailNotifications: checked }))}
                id="emailNotifications"
              />
              <ToggleRow
                label="Slack Notifications"
                description="Send alerts to configured Slack channels"
                checked={notificationSettings.slackNotifications}
                onChange={(checked) => setNotificationSettings(prev => ({ ...prev, slackNotifications: checked }))}
                id="slackNotifications"
              />
              <ToggleRow
                label="Webhook Notifications"
                description="POST alerts to custom webhook endpoints"
                checked={notificationSettings.webhookNotifications}
                onChange={(checked) => setNotificationSettings(prev => ({ ...prev, webhookNotifications: checked }))}
                id="webhookNotifications"
              />
              <ToggleRow
                label="Critical Alerts Only"
                description="Only notify for critical severity incidents"
                checked={notificationSettings.criticalAlertsOnly}
                onChange={(checked) => setNotificationSettings(prev => ({ ...prev, criticalAlertsOnly: checked }))}
                id="criticalAlertsOnly"
              />
            </div>
          </SectionCard>
        );

      case 'security':
        return (
          <SectionCard
            title="Security"
            icon={<Shield className="h-5 w-5" />}
            description="Authentication and access control settings"
          >
            <div className="space-y-5">
              <ToggleRow
                label="Two-Factor Authentication"
                description="Require 2FA for all admin accounts (UI only - requires backend implementation)"
                checked={securitySettings.twoFactorAuth}
                onChange={(checked) => setSecuritySettings(prev => ({ ...prev, twoFactorAuth: checked }))}
                id="twoFactorAuth"
              />

              <InputWithLabel
                label="Session Timeout (minutes)"
                description="Auto-logout after inactivity (5-120 min)"
                type="number"
                value={securitySettings.sessionTimeout}
                onChange={(v) => setSecuritySettings(prev => ({ ...prev, sessionTimeout: v as number }))}
                id="sessionTimeout"
                min={5}
                max={120}
              />

              <InputWithLabel
                label="Password Expiry (days)"
                description="Force password rotation (30-365 days)"
                type="number"
                value={securitySettings.passwordExpiry}
                onChange={(v) => setSecuritySettings(prev => ({ ...prev, passwordExpiry: v as number }))}
                id="passwordExpiry"
                min={30}
                max={365}
              />

              <ToggleRow
                label="Require Strong Password"
                description="Enforce complexity requirements (min 12 chars, mixed case, numbers, symbols)"
                checked={securitySettings.requireStrongPassword}
                onChange={(checked) => setSecuritySettings(prev => ({ ...prev, requireStrongPassword: checked }))}
                id="requireStrongPassword"
              />
            </div>
          </SectionCard>
        );

      case 'api':
        return (
          <SectionCard
            title="API Configuration"
            icon={<Database className="h-5 w-5" />}
            description="Backend API connection settings"
          >
            <div className="space-y-5">
              <InputWithLabel
                label="API URL"
                description="Base URL for the backend API"
                value={apiSettings.apiUrl}
                onChange={(v) => setApiSettings(prev => ({ ...prev, apiUrl: v as string }))}
                id="apiUrl"
                placeholder="Local dev uses Vite /api proxy; production uses VITE_API_BASE_URL"
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <InputWithLabel
                  label="API Timeout (seconds)"
                  description="Request timeout before aborting"
                  type="number"
                  value={apiSettings.apiTimeout}
                  onChange={(v) => setApiSettings(prev => ({ ...prev, apiTimeout: v as number }))}
                  id="apiTimeout"
                  min={5}
                  max={60}
                />

                <InputWithLabel
                  label="Retry Attempts"
                  description="Number of retries for failed requests"
                  type="number"
                  value={apiSettings.retryAttempts}
                  onChange={(v) => setApiSettings(prev => ({ ...prev, retryAttempts: v as number }))}
                  id="retryAttempts"
                  min={0}
                  max={10}
                />
              </div>

              <InputWithLabel
                label="Rate Limit (requests/minute)"
                description="Maximum API requests per minute"
                type="number"
                value={apiSettings.rateLimit}
                onChange={(v) => setApiSettings(prev => ({ ...prev, rateLimit: v as number }))}
                id="rateLimit"
                min={10}
                max={1000}
              />
            </div>
          </SectionCard>
        );

      case 'appearance':
        return (
          <SectionCard
            title="Appearance"
            icon={<Palette className="h-5 w-5" />}
            description="Customize the look and feel"
          >
            <div className="space-y-5">
              <ToggleRow
                label="Dark Mode"
                description="Switch between light and dark color schemes across the app"
                checked={darkMode}
                onChange={setDarkMode}
                id="darkMode"
              />

              <Field label="Primary Color" description="Accent color for buttons and highlights" htmlFor="primaryColor">
                <div className="flex flex-wrap gap-2" role="group" aria-label="Accent color">
                  {ACCENT_COLOR_OPTIONS.map((color) => (
                    <button
                      key={color.value}
                      type="button"
                      onClick={() => setPrimaryColor(color.value)}
                      className={`w-8 h-8 rounded-full border-2 transition-all ${
                        primaryColor.toLowerCase() === color.value.toLowerCase()
                          ? 'scale-110 ring-2 ring-offset-2 border-[var(--color-accent)] ring-[var(--color-accent)] ring-offset-[var(--app-bg)]'
                          : 'border-[var(--app-line)] hover:border-[var(--app-muted)]'
                      }`}
                      style={{ backgroundColor: color.value }}
                      aria-label={color.label}
                      aria-pressed={primaryColor.toLowerCase() === color.value.toLowerCase()}
                    />
                  ))}
                </div>
              </Field>
            </div>
          </SectionCard>
        );

      case 'account':
        return (
          <SectionCard
            title="User Account"
            icon={<User className="h-5 w-5" />}
            description="Your profile and credentials"
          >
            <div className="space-y-5">
              <InputWithLabel
                label="Email Address"
                description="Used for notifications and account recovery"
                type="email"
                value={userSettings.email}
                onChange={(v) => setUserSettings(prev => ({ ...prev, email: v as string }))}
                id="userEmail"
                placeholder="user@example.com"
              />

              <InputWithLabel
                label="Display Name"
                description="Shown in the UI and notifications"
                value={userSettings.displayName}
                onChange={(v) => setUserSettings(prev => ({ ...prev, displayName: v as string }))}
                id="userName"
                placeholder="John Doe"
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <Button variant="outline" className="w-full">
                  <Lock className="h-4 w-4 mr-2" />
                  Change Password
                </Button>
                <Button variant="outline" className="w-full">
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Enable Two-Factor Auth
                </Button>
              </div>
            </div>
          </SectionCard>
        );

      default:
        return null;
    }
  };

  return (
    <div className="page-stack">
      <PageHeader
        title="Settings"
        description="Configure preferences for this Incident Commander instance"
        actions={
          <Button onClick={handleSaveSettings} disabled={loading} className="w-full sm:w-auto">
            <Save className="h-4 w-4 mr-2" />
            {loading ? 'Saving…' : 'Save settings'}
          </Button>
        }
      />

      {/* Settings Layout - Sidebar navigation + Content */}
      <div className="settings-layout">
        {/* Left Sidebar - Section Navigation */}
        <div className="settings-nav">
          <Card className="space-y-1">
            <CardContent className="p-3 pt-2 pb-2">
              <nav aria-label="Settings sections">
                <ul className="space-y-1" role="list">
                  {settingsSections.map((section) => {
                    const Icon = section.icon;
                    const isActive = activeSection === section.id;
                    return (
                      <li key={section.id}>
                        <button
                          type="button"
                          aria-label={`${section.label} settings`}
                          onClick={() => setActiveSection(section.id as typeof activeSection)}
                          className={cn(
                            'settings-nav-btn',
                            isActive && 'settings-nav-btn-active'
                          )}
                          aria-current={isActive ? 'page' : undefined}
                        >
                          <Icon className={cn('h-5 w-5 flex-shrink-0 settings-nav-icon')} aria-hidden="true" />
                          <span className="truncate">{section.label}</span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </nav>
            </CardContent>
          </Card>

          {/* Persistence notice */}
          <Card className="info-notice mt-4">
            <CardContent className="info-notice-content">
              <HelpCircle className="info-notice-icon" />
              <div>
                <p className="info-notice-title">Settings Persistence</p>
                <p className="info-notice-text">
                  Settings are stored locally in your browser. For team-wide configuration,
                  use the backend API or environment variables. The "API URL" setting controls
                  which backend this frontend connects to.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Content - Active Section */}
        <div className="settings-content">
          {renderSection(activeSection)}
        </div>
      </div>
    </div>
  );
}