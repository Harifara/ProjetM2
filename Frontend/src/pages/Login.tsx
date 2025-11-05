import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';
import { LogIn, Mail, Lock, Eye, EyeOff, Shield, Users, BarChart3 } from 'lucide-react';
import loginBg from '@/assets/login-bg.jpg';
import logo from '@/assets/logo.jpg';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login, user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  // 🚫 Redirection si déjà connecté
  useEffect(() => {
    if (user) navigate('/dashboard');
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username || !password) {
      toast({
        title: 'Erreur',
        description: 'Veuillez remplir tous les champs',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      // 🔹 Login et récupération immédiate de l'utilisateur
      const me = await login(username, password);
      console.log('Utilisateur connecté:', me);

      toast({
        title: 'Connexion réussie',
        description: 'Bienvenue dans votre espace E.C.A.R.T',
      });

      // 🔹 Redirection immédiate
      navigate('/dashboard');
    } catch (error) {
      console.error(error);
      toast({
        title: 'Erreur de connexion',
        description: "Nom d'utilisateur ou mot de passe incorrect",
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left side */}
      <div
        className="hidden lg:flex flex-col justify-center items-center bg-gradient-primary relative overflow-hidden"
        style={{
          backgroundImage: `linear-gradient(135deg, rgba(34, 139, 34, 0.9), rgba(0, 100, 0, 0.8)), url(${loginBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="relative z-10 text-center text-white p-12 max-w-lg">
          <div className="mb-8 animate-float">
            <div className="w-60 h-60 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-strong">
              <img src={logo} alt="Logo E.C.A.R.T" className="w-120 h-120 object-contain" />
            </div>
            <h1 className="text-5xl font-bold mb-4">E.C.A.R.T</h1>
            <p className="text-xl text-white/90 mb-8">
              Espace Chrétien des Actions en Redressement de Tsihombe
            </p>
          </div>
          <div className="grid grid-cols-3 gap-6 mb-8">
            <div className="text-center animate-slide-in" style={{ animationDelay: '0.2s' }}>
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <Users className="w-6 h-6 text-white" />
              </div>
              <p className="text-sm text-white/80">Gestion des employés</p>
            </div>
            <div className="text-center animate-slide-in" style={{ animationDelay: '0.4s' }}>
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <p className="text-sm text-white/80">Analyses financières</p>
            </div>
            <div className="text-center animate-slide-in" style={{ animationDelay: '0.6s' }}>
              <div className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <p className="text-sm text-white/80">Sécurité avancée</p>
            </div>
          </div>
          <div className="text-center">
            <p className="text-white/70 text-sm">Rejoignez plus de 1000+ entreprises qui nous font confiance</p>
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center justify-center p-4 lg:p-8 bg-gradient-background min-h-screen lg:min-h-auto">
        <div className="w-full max-w-md space-y-8 animate-slide-in">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="w-24 h-24 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-strong">
              <img src={logo} alt="Logo E.C.A.R.T" className="w-120 h-120 object-contain rounded-2xl" />
            </div>
            <h1 className="text-3xl font-bold text-foreground">E.C.A.R.T</h1>
          </div>

          <Card className="shadow-medium border-0 bg-white/80 backdrop-blur-sm w-full">
            <CardContent className="p-6 lg:p-8">
              <div className="text-center mb-6 lg:mb-8">
                <h2 className="text-xl lg:text-2xl font-bold text-foreground mb-2">Connexion</h2>
                <p className="text-muted-foreground">Accédez à votre espace de travail</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4 lg:space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="username" className="text-sm font-medium">Nom utilisateur</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
                    <Input
                      id="username"
                      type="text"
                      placeholder="votre_nom_utilisateur"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="pl-12 h-12 bg-white/50 border-2 border-border/50 focus:border-primary transition-all duration-300"
                      required
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-medium">Mot de passe</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-12 pr-12 h-12 bg-white/50 border-2 border-border/50 focus:border-primary transition-all duration-300"
                      required
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" className="rounded border-border" />
                    <span className="text-muted-foreground">Se souvenir de moi</span>
                  </label>
                  <a href="#" className="text-primary hover:text-primary/80 font-medium">Mot de passe oublié ?</a>
                </div>

                <Button type="submit" variant="gradient" className="w-full h-12 text-lg font-semibold" disabled={isLoading}>
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Connexion en cours...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <LogIn className="w-5 h-5" />
                      <span>Se connecter</span>
                    </div>
                  )}
                </Button>
              </form>

              <div className="mt-8 text-center">
                <p className="text-sm text-muted-foreground">
                  Pas encore de compte ?{' '}
                  <a href="#" className="text-primary hover:text-primary/80 font-medium">Contactez votre administrateur</a>
                </p>
              </div>
            </CardContent>
          </Card>

          <div className="text-center text-xs text-muted-foreground">
            <p>© 2024 E.C.A.R.T. Tous droits réservés.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
