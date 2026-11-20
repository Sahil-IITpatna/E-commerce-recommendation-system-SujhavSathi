import React, { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { CataloguePage } from './pages/CataloguePage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { CategoryPage } from './pages/CategoryPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';

export function AppContent() {
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedProduct, setSelectedProduct] = useState(null);

  const handleSelectProductForRec = (product) => {
    setSelectedProduct(product);
    setActivePage('recommendations');
  };

  return (
    <div className="app-container">
      {/* Fixed Sidebar */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Content Area */}
      <div className="main-content">
        <Navbar
          activePage={activePage}
          onNavigateToProduct={handleSelectProductForRec}
        />

        <main style={{ flex: 1, paddingBottom: '40px' }}>
          {activePage === 'dashboard' && (
            <DashboardPage onNavigateToCatalogue={() => setActivePage('catalogue')} />
          )}

          {activePage === 'catalogue' && (
            <CataloguePage onSelectProductForRec={handleSelectProductForRec} />
          )}

          {activePage === 'recommendations' && (
            <RecommendationsPage
              selectedProduct={selectedProduct}
              onSelectProduct={setSelectedProduct}
            />
          )}

          {activePage === 'categories' && (
            <CategoryPage onSelectProductForRec={handleSelectProductForRec} />
          )}

          {activePage === 'performance' && (
            <ModelPerformancePage />
          )}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
