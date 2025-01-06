'use client';

import React, { useState } from 'react';
import { Leaf, Mail, Lock } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { auth } from '@/services/api';

const Login = () => {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (isLogin) {
        const response = await auth.login(formData.email, formData.password);
        localStorage.setItem('token', response.access_token);
        router.push('/dashboard');
      } else {
        if (formData.password !== formData.confirmPassword) {
          alert('Passwords do not match');
          return;
        }
        await auth.register(formData.email, formData.password, formData.full_name);
        // After registration, log them in automatically
        const loginResponse = await auth.login(formData.email, formData.password);
        localStorage.setItem('token', loginResponse.access_token);
        router.push('/dashboard');
      }
    } catch (error) {
      console.error('Authentication error:', error);
      alert('Authentication failed. Please check your credentials.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-stone-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
            <Leaf className="h-8 w-8 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-stone-800 mb-2">EcoPrint</h1>
          <p className="text-stone-600">Track your environmental impact</p>
        </div>

        {/* Form Container */}
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-stone-100">
          {/* Toggle */}
          <div className="flex rounded-lg bg-stone-100 p-1 mb-6">
            <button
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors
                       ${isLogin ? 'bg-white text-stone-800 shadow-sm' : 'text-stone-600'}`}
              onClick={() => setIsLogin(true)}
            >
              Login
            </button>
            <button
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors
                       ${!isLogin ? 'bg-white text-stone-800 shadow-sm' : 'text-stone-600'}`}
              onClick={() => setIsLogin(false)}
            >
              Register
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-stone-400" />
                </div>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2 border border-stone-200 rounded-lg
                           focus:ring-2 focus:ring-green-500 focus:border-transparent
                           placeholder:text-stone-400"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-stone-400" />
                  </div>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className="block w-full pl-10 pr-3 py-2 border border-stone-200 rounded-lg
                             focus:ring-2 focus:ring-green-500 focus:border-transparent
                             placeholder:text-stone-400"
                    placeholder="Enter your full name"
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-stone-700 mb-1">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-stone-400" />
                </div>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2 border border-stone-200 rounded-lg
                           focus:ring-2 focus:ring-green-500 focus:border-transparent
                           placeholder:text-stone-400"
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">
                  Confirm Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-stone-400" />
                  </div>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="block w-full pl-10 pr-3 py-2 border border-stone-200 rounded-lg
                             focus:ring-2 focus:ring-green-500 focus:border-transparent
                             placeholder:text-stone-400"
                    placeholder="Confirm your password"
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-green-600 text-white py-2 px-4 rounded-lg font-medium
                       hover:bg-green-700 transition-colors focus:ring-2 focus:ring-offset-2 
                       focus:ring-green-500"
            >
              {isLogin ? 'Sign In' : 'Create Account'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login; 